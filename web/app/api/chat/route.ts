/**
 * Chat API Proxy Route
 *
 * This route proxies chat requests to the Cloud Run backend with
 * Google Cloud IAM authentication. The service account credentials
 * are stored as an environment variable in Vercel.
 */

import { GoogleAuth } from "google-auth-library";
import { NextRequest } from "next/server";

// Cloud Run backend URL
const BACKEND_URL =
  process.env.CLOUD_RUN_BACKEND_URL ||
  "https://glass-box-backend-300347125667.us-central1.run.app";

// Initialize Google Auth with service account credentials
function getGoogleAuth(): GoogleAuth {
  const credentials = process.env.GOOGLE_SERVICE_ACCOUNT_KEY;

  if (!credentials) {
    throw new Error("GOOGLE_SERVICE_ACCOUNT_KEY environment variable not set");
  }

  // Parse the JSON credentials from the environment variable
  const parsedCredentials = JSON.parse(credentials);

  return new GoogleAuth({
    credentials: parsedCredentials,
    // The target audience is the Cloud Run service URL
    // This is required for ID token generation
  });
}

async function getIdToken(targetAudience: string): Promise<string> {
  const auth = getGoogleAuth();
  const client = await auth.getIdTokenClient(targetAudience);
  const requestHeaders = await client.getRequestHeaders();
  // getRequestHeaders returns { Authorization: string } but TypeScript types it as Headers
  const headersObj = requestHeaders as unknown as Record<string, string>;
  const authHeader = headersObj["Authorization"] || headersObj["authorization"];

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    throw new Error("Failed to get ID token");
  }

  return authHeader.substring(7); // Remove "Bearer " prefix
}

export async function POST(request: NextRequest) {
  try {
    // Get the request body
    const body = await request.text();

    // Get an ID token for the Cloud Run service
    const idToken = await getIdToken(BACKEND_URL);

    // Forward the request to Cloud Run
    const response = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${idToken}`,
      },
      body,
    });

    // Check if the response is ok
    if (!response.ok) {
      const errorText = await response.text();
      console.error("Backend error:", response.status, errorText);
      return new Response(
        JSON.stringify({
          error: "Backend request failed",
          status: response.status,
        }),
        {
          status: response.status,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // Stream the response back to the client
    // We need to pass through the streaming response from Cloud Run
    const headers = new Headers();
    response.headers.forEach((value, key) => {
      // Pass through relevant headers
      if (
        key.toLowerCase() === "content-type" ||
        key.toLowerCase().startsWith("x-")
      ) {
        headers.set(key, value);
      }
    });

    return new Response(response.body, {
      status: response.status,
      headers,
    });
  } catch (error) {
    console.error("Proxy error:", error);
    return new Response(
      JSON.stringify({
        error: "Proxy request failed",
        message: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
