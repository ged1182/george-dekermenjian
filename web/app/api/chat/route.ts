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

async function getIdToken(targetAudience: string): Promise<string> {
  try {
    const credentialsJson = process.env.GOOGLE_SERVICE_ACCOUNT_KEY;
    if (!credentialsJson) {
      throw new Error("GOOGLE_SERVICE_ACCOUNT_KEY not set");
    }

    const credentials = JSON.parse(credentialsJson);

    // Create GoogleAuth with explicit credentials
    const auth = new GoogleAuth({
      credentials: credentials,
    });

    // Get ID token client for the target audience
    const client = await auth.getIdTokenClient(targetAudience);

    // Fetch the ID token
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
