export type Role = "user" | "assistant";

export interface Citation {
  url: string;
  page?: number;
  section?: string;
}

export interface AskRequest {
  query: string;
  drug?: string;
  top_k?: number;
}

export interface AskResponse {
  answer: string;
  confidence?: number;
  contexts?: Array<{
    text: string;
    section: string;
    section_id: string;
    url: string;
    score: number;
  }>;
  drug?: string;
  disclaimer?: string;
}

export interface IngestRequest {
  drug: string;
}

export interface IngestResponse {
  drug: string;
  chunks_ingested: number;
}

export interface EvalRunRequest {
  runId?: string;
}

export interface EvalRunResponse {
  ok: boolean;
  summary?: {
    grounding_rate: number;
    citation_rate: number;
    avg_latency_ms: number;
    p50_latency_ms: number;
    p95_latency_ms: number;
  };
}

export interface HealthResponse {
  status: "healthy" | "degraded";
  redis: "connected" | "disconnected";
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  citations?: Citation[];
  confidence?: number;
  createdAt: number;
}

export interface IngestRecord {
  id: string;
  drug: string;
  chunksIngested: number;
  timestamp: number;
}
