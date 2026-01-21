import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Only handle PostHog ingest routes
  if (request.nextUrl.pathname.startsWith("/ingest")) {
    // Clone the request and strip cookies to avoid 431 errors
    const requestHeaders = new Headers(request.headers);
    requestHeaders.delete("cookie");

    // Return modified request
    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
  }

  return NextResponse.next();
}

export const config = {
  matcher: "/ingest/:path*",
};
