"use client";

import { useState, useEffect } from "react";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/fetch";
import { HealthResponse } from "@/types/api";
import { CheckCircle, AlertCircle, XCircle } from "lucide-react";

type HealthStatus = "healthy" | "degraded" | "error" | "loading";

export function HealthBadge() {
  const [status, setStatus] = useState<HealthStatus>("loading");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response: HealthResponse = await api.health();
        if (response.status === "healthy" && response.redis === "connected") {
          setStatus("healthy");
        } else {
          setStatus("degraded");
        }
      } catch (error) {
        setStatus("error");
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusConfig = () => {
    switch (status) {
      case "healthy":
        return {
          variant: "default" as const,
          icon: CheckCircle,
          text: "Healthy",
          className: "bg-green-500 hover:bg-green-600",
        };
      case "degraded":
        return {
          variant: "secondary" as const,
          icon: AlertCircle,
          text: "Degraded",
          className: "bg-yellow-500 hover:bg-yellow-600 text-white",
        };
      case "error":
        return {
          variant: "destructive" as const,
          icon: XCircle,
          text: "Offline",
          className: "bg-red-500 hover:bg-red-600",
        };
      case "loading":
        return {
          variant: "outline" as const,
          icon: AlertCircle,
          text: "Checking...",
          className: "",
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className={config.className}>
      <Icon className="h-3 w-3 mr-1" />
      {config.text}
    </Badge>
  );
}
