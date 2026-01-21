import { ImageResponse } from "next/og";

export const runtime = "edge";

export const alt = "Glass Box Portfolio - Explainable AI Systems";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#0a0a0a",
          backgroundImage:
            "radial-gradient(circle at 25% 25%, #1a1a2e 0%, transparent 50%), radial-gradient(circle at 75% 75%, #16213e 0%, transparent 50%)",
        }}
      >
        {/* Glass effect container */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: "60px 80px",
            borderRadius: "24px",
            backgroundColor: "rgba(255, 255, 255, 0.05)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            backdropFilter: "blur(10px)",
          }}
        >
          {/* Icon/Logo */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: "80px",
              height: "80px",
              borderRadius: "16px",
              backgroundColor: "rgba(59, 130, 246, 0.2)",
              border: "2px solid rgba(59, 130, 246, 0.5)",
              marginBottom: "24px",
            }}
          >
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#3b82f6"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <line x1="3" y1="9" x2="21" y2="9" />
              <line x1="9" y1="21" x2="9" y2="9" />
            </svg>
          </div>

          {/* Title */}
          <div
            style={{
              display: "flex",
              fontSize: "64px",
              fontWeight: "bold",
              color: "#ffffff",
              marginBottom: "16px",
              letterSpacing: "-0.02em",
            }}
          >
            Glass Box Portfolio
          </div>

          {/* Subtitle */}
          <div
            style={{
              display: "flex",
              fontSize: "28px",
              color: "#a1a1aa",
              textAlign: "center",
              maxWidth: "800px",
              lineHeight: 1.4,
            }}
          >
            Explainable AI Systems with Transparent Agent Reasoning
          </div>

          {/* Tags */}
          <div
            style={{
              display: "flex",
              gap: "12px",
              marginTop: "32px",
            }}
          >
            {["pydantic-ai", "Next.js", "FastAPI", "Gemini"].map((tag) => (
              <div
                key={tag}
                style={{
                  display: "flex",
                  padding: "8px 16px",
                  borderRadius: "9999px",
                  backgroundColor: "rgba(59, 130, 246, 0.15)",
                  border: "1px solid rgba(59, 130, 246, 0.3)",
                  color: "#60a5fa",
                  fontSize: "18px",
                }}
              >
                {tag}
              </div>
            ))}
          </div>
        </div>

        {/* Author */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            marginTop: "40px",
            color: "#71717a",
            fontSize: "20px",
          }}
        >
          <span>by George Dekermenjian</span>
          <span>•</span>
          <span>Director of Data & AI</span>
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
