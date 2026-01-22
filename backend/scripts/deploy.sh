#!/usr/bin/env bash
#
# Glass Box Portfolio Backend - Deployment Script
#
# This script builds locally, pushes to Artifact Registry, and deploys to Cloud Run.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Docker installed
#   - GCP project with Cloud Run and Artifact Registry APIs enabled
#   - Secret Manager secret created for GEMINI_API_KEY
#
# Usage:
#   ./scripts/deploy.sh                        # Deploy to default project
#   ./scripts/deploy.sh --project my-project   # Deploy to specific project
#   ./scripts/deploy.sh --tag v1.0.0           # Deploy with specific tag
#
# Setup (one-time):
#   1. Enable APIs:
#      gcloud services enable run.googleapis.com secretmanager.googleapis.com artifactregistry.googleapis.com
#
#   2. Create Artifact Registry repository:
#      gcloud artifacts repositories create glass-box \
#        --repository-format=docker \
#        --location=us-central1 \
#        --description="Glass Box Portfolio images"
#
#   3. Create secrets:
#      echo -n "your-gemini-api-key" | gcloud secrets create gemini-api-key --data-file=-
#      echo -n "phc_your_posthog_key" | gcloud secrets create posthog-api-key --data-file=-
#
#   4. Grant Cloud Run access to secrets:
#      PROJECT_NUMBER=$(gcloud projects describe PROJECT_ID --format='value(projectNumber)')
#      for SECRET in gemini-api-key posthog-api-key; do
#        gcloud secrets add-iam-policy-binding $SECRET \
#          --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
#          --role="roles/secretmanager.secretAccessor"
#      done

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Service name (must match cloud-run-service.yaml)
SERVICE_NAME="glass-box-backend"

# Default region (us-central1 has good pricing and availability)
REGION="${REGION:-us-central1}"

# Artifact Registry repository name
REPO_NAME="glass-box"

# Image name in Artifact Registry (will be updated with actual project ID)
IMAGE_NAME="${REGION}-docker.pkg.dev/PROJECT_ID/${REPO_NAME}/${SERVICE_NAME}"

# Script directory (for relative paths)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# -----------------------------------------------------------------------------
# Argument Parsing
# -----------------------------------------------------------------------------

PROJECT_ID=""
TAG="latest"
DRY_RUN=false
COMMIT_HASH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --project|-p)
            PROJECT_ID="$2"
            shift 2
            ;;
        --tag|-t)
            TAG="$2"
            shift 2
            ;;
        --commit|-c)
            COMMIT_HASH="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --project, -p PROJECT_ID  GCP project ID (required)"
            echo "  --tag, -t TAG             Docker image tag (default: latest)"
            echo "  --commit, -c COMMIT_HASH  Git commit hash for codebase (default: current HEAD)"
            echo "  --dry-run                 Show commands without executing"
            echo "  --help, -h                Show this help message"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Get current commit hash if not provided
if [[ -z "$COMMIT_HASH" ]]; then
    COMMIT_HASH=$(git rev-parse HEAD 2>/dev/null || echo "main")
    log_info "Using commit hash from current HEAD: ${COMMIT_HASH}"
fi

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud CLI is not installed. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID if not provided
if [[ -z "$PROJECT_ID" ]]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || true)
    if [[ -z "$PROJECT_ID" ]]; then
        log_error "No project ID specified. Use --project or set with: gcloud config set project PROJECT_ID"
        exit 1
    fi
    log_info "Using project from gcloud config: ${PROJECT_ID}"
fi

# Update image name with actual project ID
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}"

log_info "Configuration:"
log_info "  Project:  ${PROJECT_ID}"
log_info "  Service:  ${SERVICE_NAME}"
log_info "  Region:   ${REGION}"
log_info "  Image:    ${IMAGE_NAME}:${TAG}"
log_info "  Commit:   ${COMMIT_HASH}"
echo ""

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------

cd "$BACKEND_DIR"

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker to build images."
    exit 1
fi

# Build Docker image locally
log_info "Building Docker image locally..."
BUILD_CMD="docker build --build-arg CODEBASE_COMMIT_HASH=${COMMIT_HASH} -t ${IMAGE_NAME}:${TAG} ."
if [[ "$DRY_RUN" = true ]]; then
    log_info "Would run: $BUILD_CMD"
else
    $BUILD_CMD
    log_success "Image built: ${IMAGE_NAME}:${TAG}"
fi

# -----------------------------------------------------------------------------
# Push to Artifact Registry
# -----------------------------------------------------------------------------

log_info "Pushing image to Artifact Registry..."

# Configure docker for Artifact Registry
if [[ "$DRY_RUN" = true ]]; then
    log_info "Would run: gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet"
else
    gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet
fi

PUSH_CMD="docker push ${IMAGE_NAME}:${TAG}"
if [[ "$DRY_RUN" = true ]]; then
    log_info "Would run: $PUSH_CMD"
else
    $PUSH_CMD
    log_success "Image pushed to Artifact Registry"
fi

# -----------------------------------------------------------------------------
# Deploy
# -----------------------------------------------------------------------------

log_info "Deploying to Cloud Run..."

# Deploy using gcloud run deploy with inline configuration
# Note: Service requires authentication (no --allow-unauthenticated flag)
DEPLOY_CMD="gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:${TAG} \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --platform managed \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 1 \
    --max-instances 3 \
    --concurrency 80 \
    --timeout 300 \
    --set-secrets=GEMINI_API_KEY=gemini-api-key:latest,POSTHOG_API_KEY=posthog-api-key:latest \
    --set-env-vars=ENVIRONMENT=production,POSTHOG_HOST=https://eu.i.posthog.com \
    --no-allow-unauthenticated"

if [[ "$DRY_RUN" = true ]]; then
    log_info "Would run: $DEPLOY_CMD"
else
    eval "$DEPLOY_CMD"
    log_success "Service deployed to Cloud Run (requires authentication)"
fi

# -----------------------------------------------------------------------------
# Output
# -----------------------------------------------------------------------------

if [[ "$DRY_RUN" = false ]]; then
    echo ""
    log_success "Deployment complete!"
    echo ""

    # Get the service URL
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
        --region ${REGION} \
        --project ${PROJECT_ID} \
        --format 'value(status.url)' 2>/dev/null || true)

    if [[ -n "$SERVICE_URL" ]]; then
        log_info "Service URL: ${SERVICE_URL}"
        log_info "Health check: ${SERVICE_URL}/health"
        log_info "API docs: ${SERVICE_URL}/docs"
    fi

    echo ""
    log_info "Next steps:"
    echo "  1. Update your frontend NEXT_PUBLIC_BACKEND_URL to: ${SERVICE_URL}"
    echo "  2. Verify the health endpoint: curl ${SERVICE_URL}/health"
    echo "  3. Check logs: gcloud run logs read ${SERVICE_NAME} --region ${REGION}"
fi
