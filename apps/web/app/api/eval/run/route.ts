import { NextRequest, NextResponse } from "next/server";
import { env } from "@/lib/env";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const response = await fetch(`${env.NEXT_PUBLIC_API_BASE}/eval/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(env.NEXT_PUBLIC_API_KEY && {
          "Authorization": `Bearer ${env.NEXT_PUBLIC_API_KEY}`,
        }),
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `HTTP ${response.status}: ${errorText}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Proxy error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
