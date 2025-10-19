"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { api } from "@/lib/fetch";
import { EvalRunResponse } from "@/types/api";
import { BarChart3, Play, CheckCircle, XCircle } from "lucide-react";

export default function EvalsPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<EvalRunResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunEval = async () => {
    setIsRunning(true);
    setError(null);
    setResults(null);

    try {
      const response = await api.evalRun();
      setResults(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run evaluation");
    } finally {
      setIsRunning(false);
    }
  };

  const formatMetric = (value: number, suffix: string = "") => {
    if (suffix === "%") {
      return `${(value * 100).toFixed(1)}%`;
    }
    return `${value.toFixed(1)}${suffix}`;
  };

  return (
    <div className="container mx-auto max-w-4xl p-4">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">System Evaluation</h1>
          <p className="text-muted-foreground">
            Run performance evaluations on the RAG system
          </p>
        </div>

        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              <h2 className="text-xl font-semibold">Run Evaluation</h2>
            </div>

            <p className="text-sm text-muted-foreground">
              This will run a comprehensive evaluation suite to measure system performance including grounding rate, citation rate, and latency metrics.
            </p>

            <Button
              onClick={handleRunEval}
              disabled={isRunning}
              className="w-full sm:w-auto"
            >
              {isRunning ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent mr-2" />
                  Running Evaluation...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Run Evaluation
                </>
              )}
            </Button>
          </div>
        </Card>

        {error && (
          <Card className="p-6 border-destructive">
            <div className="flex items-center gap-2 text-destructive">
              <XCircle className="h-5 w-5" />
              <h3 className="font-semibold">Evaluation Failed</h3>
            </div>
            <p className="text-sm text-muted-foreground mt-2">{error}</p>
          </Card>
        )}

        {results && (
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <h2 className="text-xl font-semibold">Evaluation Results</h2>
              </div>

              {results.summary ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">Grounding Rate</Badge>
                      </div>
                      <p className="text-2xl font-bold">
                        {formatMetric(results.summary.grounding_rate, "%")}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Queries properly grounded in source material
                      </p>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">Citation Rate</Badge>
                      </div>
                      <p className="text-2xl font-bold">
                        {formatMetric(results.summary.citation_rate, "%")}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Responses include proper citations
                      </p>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">Avg Latency</Badge>
                      </div>
                      <p className="text-2xl font-bold">
                        {formatMetric(results.summary.avg_latency_ms, "ms")}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Average response time
                      </p>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">P50 Latency</Badge>
                      </div>
                      <p className="text-2xl font-bold">
                        {formatMetric(results.summary.p50_latency_ms, "ms")}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Median response time
                      </p>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">P95 Latency</Badge>
                      </div>
                      <p className="text-2xl font-bold">
                        {formatMetric(results.summary.p95_latency_ms, "ms")}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        95th percentile response time
                      </p>
                    </div>
                  </div>

                  <div className="mt-6">
                    <h3 className="font-semibold mb-2">Raw Results</h3>
                    <ScrollArea className="h-64 w-full border rounded-lg">
                      <pre className="p-4 text-sm">
                        {JSON.stringify(results, null, 2)}
                      </pre>
                    </ScrollArea>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-500" />
                  <p className="text-muted-foreground">
                    Evaluation completed successfully. Check the logs for detailed results.
                  </p>
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
