"use client";

import { useEffect, useMemo, useState } from "react";

type Item = {
  id: number;
  source: string;
  title: string;
  url: string;
  published_at: string | null;
  fetched_at: string;
};

type ApiResponse = {
  page: number;
  page_size: number;
  total: number;
  items: Item[];
};

export default function Home() {
  const [q, setQ] = useState("");
  const [debouncedQ, setDebouncedQ] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const [data, setData] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  // debounce so we don't call the API on every keystroke
  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(q), 350);
    return () => clearTimeout(t);
  }, [q]);

  // Browser runs on your Mac, so use localhost:8000 here
  const endpoint = useMemo(() => {
    const base = "http://localhost:8000/items";
    const params = new URLSearchParams();
    params.set("page", String(page));
    params.set("page_size", String(pageSize));
    if (debouncedQ.trim()) params.set("q", debouncedQ.trim());
    return `${base}?${params.toString()}`;
  }, [debouncedQ, page]);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      setLoading(true);
      setErr(null);
      try {
        const res = await fetch(endpoint);
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        const json = (await res.json()) as ApiResponse;
        if (!cancelled) setData(json);
      } catch (e: any) {
        if (!cancelled) setErr(e?.message || "Unknown error");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    run();
    return () => {
      cancelled = true;
    };
  }, [endpoint]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  return (
    <main style={{ maxWidth: 920, margin: "0 auto", padding: 24, fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 6 }}>SignalStack</h1>
      <p style={{ marginTop: 0, color: "#666", marginBottom: 18 }}>
        Live feed demo (worker → Postgres → FastAPI → Next.js)
      </p>

      <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 16 }}>
        <input
          value={q}
          onChange={(e) => {
            setPage(1);
            setQ(e.target.value);
          }}
          placeholder="Search titles or sources…"
          style={{
            flex: 1,
            padding: "10px 12px",
            border: "1px solid #ddd",
            borderRadius: 10,
            outline: "none",
          }}
        />
        <button
          onClick={() => setQ("")}
          style={{
            padding: "10px 12px",
            border: "1px solid #ddd",
            borderRadius: 10,
            background: "white",
            cursor: "pointer",
          }}
        >
          Clear
        </button>
      </div>

      <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 14 }}>
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1 || loading}
          style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          ◀ Prev
        </button>
        <div style={{ color: "#666" }}>
          Page <b>{page}</b> / <b>{totalPages}</b> {data ? `• ${data.total} items` : ""}
        </div>
        <button
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page >= totalPages || loading}
          style={{ padding: "8px 10px", borderRadius: 10, border: "1px solid #ddd", background: "white", cursor: "pointer" }}
        >
          Next ▶
        </button>
      </div>

      {err && (
        <div style={{ padding: 12, border: "1px solid #f3b0b0", borderRadius: 10, background: "#fff5f5", marginBottom: 14 }}>
          <b>Error:</b> {err}
        </div>
      )}

      {loading && <div style={{ color: "#666" }}>Loading…</div>}

      <ul style={{ listStyle: "none", padding: 0, marginTop: 12 }}>
        {data?.items?.map((it) => (
          <li key={it.id} style={{ padding: "12px 0", borderBottom: "1px solid #eee" }}>
            <div style={{ fontSize: 12, color: "#666", marginBottom: 6 }}>{it.source}</div>
            <a href={it.url} target="_blank" rel="noreferrer" style={{ fontSize: 16, fontWeight: 600, color: "#111" }}>
              {it.title}
            </a>
          </li>
        ))}
      </ul>
    </main>
  );
}

