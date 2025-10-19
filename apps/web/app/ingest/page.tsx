"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api } from "@/lib/fetch";
import { IngestRecord } from "@/types/api";
import { Database, Upload, Clock } from "lucide-react";

const INGEST_STORAGE_KEY = "med-rag-ingests";

export default function IngestPage() {
  const [drug, setDrug] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [ingests, setIngests] = useState<IngestRecord[]>([]);

  // Load ingests from localStorage on mount
  useEffect(() => {
    const savedIngests = localStorage.getItem(INGEST_STORAGE_KEY);
    if (savedIngests) {
      try {
        setIngests(JSON.parse(savedIngests));
      } catch (error) {
        console.error("Failed to parse saved ingests:", error);
      }
    }
  }, []);

  // Save ingests to localStorage whenever ingests change
  useEffect(() => {
    localStorage.setItem(INGEST_STORAGE_KEY, JSON.stringify(ingests));
  }, [ingests]);

  const handleIngest = async () => {
    if (!drug.trim() || isLoading) return;

    setIsLoading(true);
    try {
      const response = await api.ingest({ drug: drug.trim() });

      const newIngest: IngestRecord = {
        id: Date.now().toString(),
        drug: response.drug,
        chunksIngested: response.chunks_ingested,
        timestamp: Date.now(),
      };

      setIngests(prev => [newIngest, ...prev.slice(0, 9)]); // Keep last 10
      setDrug("");
    } catch (error) {
      console.error("Failed to ingest drug:", error);
      alert("Failed to ingest drug. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleIngest();
    }
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="container mx-auto max-w-4xl p-4">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Drug Ingestion</h1>
          <p className="text-muted-foreground">
            Ingest medication label data into the knowledge base
          </p>
        </div>

        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              <h2 className="text-xl font-semibold">Ingest New Drug</h2>
            </div>

            <div className="flex gap-2">
              <Input
                placeholder="Enter drug name (e.g., metformin, aspirin)"
                value={drug}
                onChange={(e) => setDrug(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                onClick={handleIngest}
                disabled={!drug.trim() || isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent mr-2" />
                    Ingesting...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Ingest
                  </>
                )}
              </Button>
            </div>

            <p className="text-sm text-muted-foreground">
              This will fetch and process the latest medication label data from DailyMed
            </p>
          </div>
        </Card>

        {ingests.length > 0 && (
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                <h2 className="text-xl font-semibold">Recent Ingests</h2>
              </div>

              <div className="space-y-3">
                {ingests.map((ingest) => (
                  <div
                    key={ingest.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <Badge variant="outline">{ingest.drug}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {ingest.chunksIngested} chunks ingested
                      </span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {formatTimestamp(ingest.timestamp)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
