"use client";
import { useLang } from "@/lib/i18n";

const PRESET_IDS = ["A", "B", "C", "D"] as const;

export function Presets() {
  const { t } = useLang();
  const th = t.presets;

  return (
    <section className="py-32 px-6 max-w-5xl mx-auto scroll-mt-20">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        {th.title}{" "}
        <span style={{ color: "var(--color-muted)" }}>{th.titleSub}</span>
      </h2>
      <p className="mt-4 max-w-2xl" style={{ color: "var(--color-muted)" }}>
        {th.subtitle}
      </p>
      <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4">
        {th.items.map((p, i) => (
          <div
            key={PRESET_IDS[i]}
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
                {PRESET_IDS[i]}
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
