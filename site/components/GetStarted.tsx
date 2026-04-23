"use client";
import { useLang } from "@/lib/i18n";

export function GetStarted() {
  const { t } = useLang();
  const th = t.getStarted;

  return (
    <section id="get-started" className="py-32 px-6 max-w-5xl mx-auto scroll-mt-20">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        {th.title}
      </h2>
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-4">
        {th.cards.map((c) => (
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
