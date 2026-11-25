// Public edge for the credit API: CORS lock + rate limit + proxy to the HF Space (FastAPI). No model code here.
export interface Env {
  ORIGIN_URL: string; // https://<user>-<space>.hf.space
  ALLOWED_ORIGIN: string; // https://<project>.pages.dev
  RL?: { limit(o: { key: string }): Promise<{ success: boolean }> };
}

const json = (body: unknown, status: number, h: HeadersInit = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json", ...h } });

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const cors = {
      "Access-Control-Allow-Origin": env.ALLOWED_ORIGIN,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      Vary: "Origin",
    };
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

    const url = new URL(req.url);
    if (!(url.pathname === "/health" || url.pathname.startsWith("/bank/"))) return json({ detail: "not found" }, 404, cors);
    if (req.method !== "GET" && req.method !== "POST") return json({ detail: "method not allowed" }, 405, cors);

    // PIN lookup is enumerable (7 chars): limit per client IP
    const ip = req.headers.get("CF-Connecting-IP") ?? "unknown";
    if (env.RL && !(await env.RL.limit({ key: ip })).success) return json({ detail: "too many requests" }, 429, cors);

    try {
      const upstream = await fetch(new URL(url.pathname + url.search, env.ORIGIN_URL), {
        method: req.method,
        headers: { "Content-Type": req.headers.get("Content-Type") ?? "application/json" },
        body: req.method === "POST" ? req.body : undefined,
        signal: AbortSignal.timeout(25_000),
      });
      const h = new Headers(upstream.headers);
      for (const [k, v] of Object.entries(cors)) h.set(k, v);
      return new Response(upstream.body, { status: upstream.status, headers: h });
    } catch {
      // Space sleeps when idle; first request wakes it (30-60 s)
      return json({ detail: "service is waking up, retry in a minute" }, 503, { ...cors, "Retry-After": "30" });
    }
  },
};
