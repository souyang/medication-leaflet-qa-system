"use client";

import { Citation } from "@/types/api";
import { Badge } from "@/components/ui/badge";
import { ExternalLink } from "lucide-react";

interface CitationsListProps {
  citations: Citation[];
}

export function CitationsList({ citations }: CitationsListProps) {
  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium">Sources:</h4>
      <div className="flex flex-wrap gap-2">
        {citations.map((citation, index) => (
          <Badge
            key={index}
            variant="outline"
            className="cursor-pointer hover:bg-accent"
            onClick={() => window.open(citation.url, "_blank", "noopener,noreferrer")}
          >
            <ExternalLink className="h-3 w-3 mr-1" />
            {citation.section || `Source ${index + 1}`}
          </Badge>
        ))}
      </div>
    </div>
  );
}
