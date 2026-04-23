const cards = [
  {
    title: "API",
    body: "Full L1 + Multi_L via FastAPI. Any client, any language.",
    cta: "uvicorn api.main:app --reload",
  },
  {
    title: "Web chat",
    body: "Copy a plugin prompt into ChatGPT, Claude, Gemini, or Grok. L1 only.",
    cta: "norag/plugins/<provider>.md",
  },
  {
    title: "Claude Code skill",
    body: "Use /norag directly in your terminal. L1 + Multi_L, reads local files.",
    cta: "/norag <question>",
  },
];

export function GetStarted() {
  return (
    <section className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        Get started.
      </h2>
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((c) => (
          <div
            key={c.title}
            className="p-6 rounded-xl"
            style={{
              background: "var(--color-bg-surface)",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <div className="text-xl font-medium">{c.title}</div>
            <p className="mt-3" style={{ color: "var(--color-muted)" }}>
              {c.body}
            </p>
            <div
              className="mt-4 text-xs font-mono"
              style={{ color: "var(--color-accent)" }}
            >
              {c.cta}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
