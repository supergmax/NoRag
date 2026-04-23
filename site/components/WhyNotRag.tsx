const rows = [
  { k: "Infrastructure", rag: "Vector DB + embedding model", norag: "Plain Markdown files" },
  { k: "Cost of adding a doc", rag: "Recurring (re-embed + storage)", norag: "One-shot archivist pass" },
  { k: "Context given to LLM", rag: "Arbitrary chunks", norag: "Complete sections" },
  { k: "Auditability", rag: "Opaque vectors", norag: "Git-diffable Markdown" },
  { k: "Citations", rag: "Approximate", norag: "Precise [doc_id, section]" },
  { k: "Who fixes the index?", rag: "Data scientist", norag: "Any dev who reads MD" },
];

export function WhyNotRag() {
  return (
    <section className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        Why not{" "}
        <span className="line-through" style={{ color: "var(--color-muted)" }}>
          RAG
        </span>
        .
      </h2>
      <p className="mt-4 max-w-2xl" style={{ color: "var(--color-muted)" }}>
        Vectors are opaque, chunks are arbitrary, and ingestion keeps paying.
        NoRag swaps the whole stack for Markdown the LLM can read directly.
      </p>

      <div className="mt-16 border rounded-2xl overflow-hidden" style={{ borderColor: "rgba(255,255,255,0.1)" }}>
        <div className="grid grid-cols-3 text-sm">
          {["Criterion", "RAG", "NoRag"].map((h, i) => (
            <div
              key={h}
              className="p-4"
              style={{
                background: "var(--color-bg-surface)",
                color: i === 2 ? "var(--color-accent)" : "var(--color-muted)",
              }}
            >
              {h}
            </div>
          ))}
          {rows.map((r) => (
            <>
              <div key={r.k + "k"} className="p-4" style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>{r.k}</div>
              <div key={r.k + "r"} className="p-4" style={{ borderTop: "1px solid rgba(255,255,255,0.05)", color: "var(--color-muted)" }}>{r.rag}</div>
              <div key={r.k + "n"} className="p-4" style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>{r.norag}</div>
            </>
          ))}
        </div>
      </div>
    </section>
  );
}
