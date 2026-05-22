/**
 * Backend client.
 *
 * Talks to the FastAPI server in panel/api/server.py. Falls back to the
 * MOCK_RESULT when the server is unreachable so the v2 still demos cleanly
 * during development.
 *
 * Resolves the base URL from VITE_API_BASE (env-time) or defaults to
 * http://localhost:8000 in dev.
 */
import { MOCK_RESULT } from "./mock-result";
import type { PanelResult } from "./mock-result";

// Empty base = relative URLs (works when frontend + API are same-origin —
// either Databricks Apps deploy or Vite dev with the proxy in vite.config.ts).
// Override with VITE_API_BASE if pointing at a separate FastAPI host.
const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";

export type RunRequest = {
  sample_id?: string;
  contract_text?: string;
  situation?: string;
  destination_country: string;
  origin_country: string;
  worker_l1: string;
};

export async function runPanel(req: RunRequest, opts: { timeoutMs?: number } = {}): Promise<PanelResult> {
  const ac = new AbortController();
  const timer = window.setTimeout(() => ac.abort(), opts.timeoutMs ?? 300_000);
  try {
    const res = await fetch(`${API_BASE}/api/panel/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
      signal: ac.signal,
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    return (await res.json()) as PanelResult;
  } finally {
    window.clearTimeout(timer);
  }
}

export async function runPanelWithFallback(req: RunRequest): Promise<{
  result: PanelResult;
  source: "live" | "mock";
}> {
  try {
    const result = await runPanel(req, { timeoutMs: 240_000 });
    return { result, source: "live" };
  } catch (e) {
    console.warn("[panel] backend unreachable, using mock:", e);
    return { result: MOCK_RESULT, source: "mock" };
  }
}

export async function isBackendUp(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`, {
      signal: AbortSignal.timeout(2000),
    });
    return res.ok;
  } catch {
    return false;
  }
}
