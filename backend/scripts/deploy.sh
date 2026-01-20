#!/usr/bin/env bash
#
# Glass Box Portfolio Backend - Deployment Script
#
# This script builds and deploys the backend to Google Cloud Run.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Docker installed (for local builds)
#   - GCP project with Cloud Run API enabled
#   - Secret Manager secret created for GEMINI_API_KEY
#
# Usage:
#   ./scripts/deploy.sh              # Deploy to default project
#   ./scripts/deploy.sh --project my-project  # Deploy to specific project
#   ./scripts/deploy.sh --local      # Build locally instead of Cloud Build
#
# Setup (one-time):
#   1. Enable APIs:
#      gcloud services enable run.googleapis.com secretmanager.googleapis.com
#
#   2. Create secret:
#      echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-
#
#   3. Grant Cloud Run access to secret:
#      gcloud secrets add-iam-policy-binding gemini-api-key \
#        --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
#        --role="roles/secretmanager.secretAccessor"

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

# Service name (must match cloud-run-service.yaml)
SERVICE_NAME="glass-box-backend"

# Default region (us-central1 has good pricing and availability)
REGION="${REGION:-us-central1}"

# Image name in Google Container Registry
IMAGE_NAME="gcr.io/${PROJECT_ID:-PROJECT_ID}/${SERVICE_NAME}"

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
LOCAL_BUILD=false
TAG="latest"
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --project|-p)
            PROJECT_ID="$2"
            shift 2
            ;;
        --local|-l)
            LOCAL_BUILD=true
            shift
            ;;
        --tag|-t)
            TAG="$2"
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
            echo "  --local, -l               Build locally instead of Cloud Build"
            echo "  --tag, -t TAG             Docker image tag (default: latest)"
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
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

log_info "Configuration:"
log_info "  Project:  ${PROJECT_ID}"
log_info "  Service:  ${SERVICE_NAME}"
log_info "  Region:   ${REGION}"
log_info "  Image:    ${IMAGE_NAME}:${TAG}"
log_info "  Build:    $([ "$LOCAL_BUILD" = true ] && echo 'Local' || echo 'Cloud Build')"
echo ""

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------

cd "$BACKEND_DIR"

if [[ "$LOCAL_BUILD" = true ]]; then
    # Local build with docker
    log_info "Building Docker image locally..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed for local builds."
        exit 1
    fi

    BUILD_CMD="docker build -t ${IMAGE_NAME}:${TAG} ."
    if [[ "$DRY_RUN" = true ]]; then
        log_info "Would run: $BUILD_CMD"
    else
        $BUILD_CMD
        log_success "Image built: ${IMAGE_NAME}:${TAG}"
    fi

    # Push to GCR
    log_info "Pushing image to Google Container Registry..."
    PUSH_CMD="docker push ${IMAGE_NAME}:${TAG}"
    if [[ "$DRY_RUN" = true ]]; then
        log_info "Would run: $PUSH_CMD"
    else
        # Configure docker for GCR
        gcloud auth configure-docker gcr.io --quiet
        $PUSH_CMD
        log_success "Image pushed to GCR"
    fi
else
    # Cloud Build
    log_info "Building with Google Cloud Build..."
    BUILD_CMD="gcloud builds submit --tag ${IMAGE_NAME}:${TAG} --project ${PROJECT_ID} ."
    if [[ "$DRY_RUN" = true ]]; then
        log_info "Would run: $BUILD_CMD"
    else
        $BUILD_CMD
        log_success "Image built and pushed via Cloud Build"
    fi
fi

# -----------------------------------------------------------------------------
# Deploy
# -----------------------------------------------------------------------------

log_info "Deploying to Cloud Run..."

# Create a temporary service config with the actual project ID
TEMP_CONFIG=$(mktemp)
sed "s/PROJECT_ID/${PROJECT_ID}/g" cloud-run-service.yaml > "$TEMP_CONFIG"

# Also update the image tag
sed -i "s/:latest/:${TAG}/g" "$TEMP_CONFIG"

DEPLOY_CMD="gcloud run services replace ${TEMP_CONFIG} --region ${REGION} --project ${PROJECT_ID}"

if [[ "$DRY_RUN" = true ]]; then
    log_info "Would run: $DEPLOY_CMD"
    log_info "With config:"
    cat "$TEMP_CONFIG"
else
    $DEPLOY_CMD
    log_success "Service deployed to Cloud Run"
fi

# Cleanup
rm -f "$TEMP_CONFIG"

# -----------------------------------------------------------------------------
# Make service publicly accessible
# -----------------------------------------------------------------------------

log_info "Configuring IAM policy for public access..."

IAM_CMD="gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
    --region ${REGION} \
    --project ${PROJECT_ID} \
    --member=\"allUsers\" \
    --role=\"roles/run.invoker\""

if [[ "$DRY_RUN" = true ]]; then
    log_info "Would run: $IAM_CMD"
else
    eval "$IAM_CMD" > /dev/null
    log_success "Public access configured"
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
