"use client";
import React from "react";
import { useLang } from "@/lib/i18n";

export function WhyNotRag() {
  const { t } = useLang();
  const th = t.whyNotRag;

  return (
    <section id="comparison" className="py-32 px-6 max-w-5xl mx-auto scroll-mt-20">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        {th.title}{" "}
        <span className="line-through" style={{ color: "var(--color-muted)" }}>
          RAG
        </span>
        .
      </h2>
      <p className="mt-4 max-w-2xl" style={{ color: "var(--color-muted)" }}>
        {th.subtitle}
      </p>

      <div
        className="mt-16 border rounded-2xl overflow-x-auto"
        style={{ borderColor: "rgba(255,255,255,0.1)" }}
      >
        <div className="grid grid-cols-3 text-sm min-w-[480px]">
          {th.headers.map((h, i) => (
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
          {th.rows.map((r) => (
            <React.Fragment key={r.k}>
              <div className="p-4" style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
                {r.k}
              </div>
              <div
                className="p-4"
                style={{ borderTop: "1px solid rgba(255,255,255,0.05)", color: "var(--color-muted)" }}
              >
                {r.rag}
              </div>
              <div className="p-4" style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
                {r.norag}
              </div>
            </React.Fragment>
          ))}
        </div>
      </div>
    </section>
  );
}
