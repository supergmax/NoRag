"use client";
import { useLang } from "@/lib/i18n";

export function UnderTheHoodClient({
  indexHtml,
  agentsHtml,
}: {
  indexHtml: string;
  agentsHtml: string;
}) {
  const { t } = useLang();
  const th = t.underTheHood;

  return (
    <section className="py-32 px-6 max-w-5xl mx-auto scroll-mt-20">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        {th.title}
      </h2>
      <p className="mt-4 max-w-2xl" style={{ color: "var(--color-muted)" }}>
        {th.subtitle}
      </p>
      <div className="mt-12 grid md:grid-cols-2 gap-6">
        <div>
          <div
            className="text-sm mb-2 font-mono"
            style={{ color: "var(--color-muted)" }}
          >
            data/index.md
          </div>
          <div
            className="rounded-xl overflow-hidden text-sm"
            style={{ border: "1px solid rgba(255,255,255,0.1)" }}
            dangerouslySetInnerHTML={{ __html: indexHtml }}
          />
        </div>
        <div>
          <div
            className="text-sm mb-2 font-mono"
            style={{ color: "var(--color-muted)" }}
          >
            data/index_system_prompt.md
          </div>
          <div
            className="rounded-xl overflow-hidden text-sm"
            style={{ border: "1px solid rgba(255,255,255,0.1)" }}
            dangerouslySetInnerHTML={{ __html: agentsHtml }}
          />
        </div>
      </div>
    </section>
  );
}
