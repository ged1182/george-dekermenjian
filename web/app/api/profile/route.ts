/**
 * Profile API Proxy Route
 *
 * This route proxies profile requests to the Cloud Run backend with
 * Google Cloud IAM authentication.
 */

import { GoogleAuth } from "google-auth-library";
import { NextRequest } from "next/server";

// Cloud Run backend URL
const BACKEND_URL =
  process.env.CLOUD_RUN_BACKEND_URL ||
  "https://glass-box-backend-300347125667.us-central1.run.app";

async function getIdToken(targetAudience: string): Promise<string> {
  try {
    const credentialsJson = process.env.GOOGLE_SERVICE_ACCOUNT_KEY;
    if (!credentialsJson) {
      throw new Error("GOOGLE_SERVICE_ACCOUNT_KEY not set");
    }

    const credentials = JSON.parse(credentialsJson);

    const auth = new GoogleAuth({
      credentials: credentials,
    });

    const client = await auth.getIdTokenClient(targetAudience);
    const token = await client.idTokenProvider.fetchIdToken(targetAudience);

    if (!token) {
      throw new Error("No ID token returned from Google Auth");
    }

    return token;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    console.error("getIdToken error:", message);
    throw new Error(`Failed to get ID token: ${message}`);
  }
}

export async function GET(_request: NextRequest) {
  try {
    // Get an ID token for the Cloud Run service
    const idToken = await getIdToken(BACKEND_URL);

    // Forward the request to Cloud Run
    const response = await fetch(`${BACKEND_URL}/profile`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${idToken}`,
      },
      // Disable caching to ensure fresh data
      cache: "no-store",
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

    // Return the JSON response
    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        // Prevent caching issues
        "Cache-Control": "no-cache, no-store, must-revalidate",
      },
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
