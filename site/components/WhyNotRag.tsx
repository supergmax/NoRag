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

      {/* Mobile: card layout */}
      <div className="mt-16 md:hidden space-y-3">
        {th.rows.map((r) => (
          <div
            key={r.k}
            className="rounded-xl overflow-hidden"
            style={{ border: "1px solid rgba(255,255,255,0.1)" }}
          >
            <div
              className="px-4 py-3 text-sm font-medium"
              style={{ background: "var(--color-bg-surface)" }}
            >
              {r.k}
            </div>
            <div className="grid grid-cols-2 text-xs" style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}>
              <div
                className="px-4 py-3 border-r"
                style={{ borderColor: "rgba(255,255,255,0.08)", color: "var(--color-muted)" }}
              >
                <div className="mb-1 opacity-60 text-[10px] uppercase tracking-wide">{th.headers[1]}</div>
                {r.rag}
              </div>
              <div className="px-4 py-3" style={{ color: "var(--color-accent)" }}>
                <div className="mb-1 opacity-60 text-[10px] uppercase tracking-wide">{th.headers[2]}</div>
                {r.norag}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Desktop: grid table */}
      <div
        className="hidden md:block mt-16 border rounded-2xl overflow-hidden"
        style={{ borderColor: "rgba(255,255,255,0.1)" }}
      >
        <div className="grid grid-cols-3 text-sm">
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
