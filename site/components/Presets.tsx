const presets = [
  {
    id: "A",
    title: "Multi-Agent",
    body: "Same question, different agents. Cross-perspectives in one response.",
    example: "Layer 1: juriste_conformite\nLayer 2: analyste_technique\nLayer 3: analyste_finance",
  },
  {
    id: "B",
    title: "Decomposition",
    body: "Split the question into sub-questions routed independently.",
    example: 'L1: "AWS cloud strategy 2020-2024"\nL2: "Azure cloud strategy 2020-2024"',
  },
  {
    id: "C",
    title: "Multi-Corpus",
    body: "Same question, different agents, different document scopes.",
    example: "L1: juriste, scope=contrats\nL2: analyste_technique, scope=doc_technique",
  },
  {
    id: "D",
    title: "Hybrid / Auto",
    body: "Planner freely combines agents, sub-questions, and index scopes.",
    example: "Let the Planner decide.",
  },
];

export function Presets() {
  return (
    <section className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        Four presets.{" "}
        <span style={{ color: "var(--color-muted)" }}>Same engine.</span>
      </h2>
      <p className="mt-4 max-w-2xl" style={{ color: "var(--color-muted)" }}>
        Configure Multi_L for your use case by picking a preset — or let the
        Planner decide automatically.
      </p>
      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4">
        {presets.map((p) => (
          <div
            key={p.id}
            className="p-6 rounded-xl transition-all"
            style={{
              background: "var(--color-bg-surface)",
              border: "1px solid rgba(255,255,255,0.1)",
            }}
          >
            <div className="flex items-baseline gap-3">
              <span
                className="text-3xl font-semibold"
                style={{ color: "var(--color-accent)" }}
              >
                {p.id}
              </span>
              <span className="text-xl font-medium">{p.title}</span>
            </div>
            <p className="mt-3" style={{ color: "var(--color-muted)" }}>
              {p.body}
            </p>
            <pre
              className="mt-4 text-xs whitespace-pre-wrap"
              style={{ color: "rgba(255,255,255,0.6)" }}
            >
              {p.example}
            </pre>
          </div>
        ))}
      </div>
    </section>
  );
}
