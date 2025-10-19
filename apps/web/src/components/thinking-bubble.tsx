"use client";

import { Card } from "@/components/ui/card";
import { Bot } from "lucide-react";

export function ThinkingBubble() {
  return (
    <div className="flex gap-3 justify-start">
      <div className="flex gap-3 max-w-[80%]">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted">
          <Bot className="h-4 w-4" />
        </div>

        <Card className="p-4 bg-muted">
          <div className="flex items-center gap-2">
            <div className="flex space-x-1">
              <div className="h-2 w-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              <div className="h-2 w-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:-0.15s]"></div>
              <div className="h-2 w-2 bg-muted-foreground rounded-full animate-bounce"></div>
            </div>
            <span className="text-sm text-muted-foreground">Thinking...</span>
          </div>
        </Card>
      </div>
    </div>
  );
}
