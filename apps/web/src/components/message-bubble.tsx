"use client";

import { Message, Citation } from "@/types/api";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CopyButton } from "@/components/copy-button";
import { CitationsList } from "@/components/citations-list";
import { cn } from "@/lib/utils";
import { User, Bot } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3", isUser ? "justify-end" : "justify-start")}>
      <div className={cn("flex gap-3 max-w-[80%]", isUser ? "flex-row-reverse" : "flex-row")}>
        <div className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}>
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </div>

        <Card className={cn(
          "p-4",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}>
          <div className="prose prose-sm max-w-none">
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>

          {message.confidence && (
            <div className="mt-2">
              <Badge variant="secondary" className="text-xs">
                Confidence: {Math.round(message.confidence * 100)}%
              </Badge>
            </div>
          )}

          {message.citations && message.citations.length > 0 && (
            <div className="mt-3">
              <CitationsList citations={message.citations} />
            </div>
          )}

          <div className="mt-3 flex justify-end">
            <CopyButton text={message.content} />
          </div>
        </Card>
      </div>
    </div>
  );
}
