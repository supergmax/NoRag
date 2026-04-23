"use client";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { useLang } from "@/lib/i18n";

const LAYERS = [
  { id: 1, agent: "juriste_conformite",  color: "var(--color-accent)" },
  { id: 2, agent: "analyste_technique",  color: "var(--color-accent-2)" },
  { id: 3, agent: "analyste_finance",    color: "#e879f9" },
];

export function MultiLDemo() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: false, margin: "-30% 0px" });
  const { t } = useLang();
  const th = t.multiLDemo;

  return (
    <section id="multil" ref={ref} className="py-32 px-6 max-w-5xl mx-auto scroll-mt-20">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        {th.title}{" "}
        <span style={{ color: "var(--color-muted)" }}>{th.titleSub}</span>
      </h2>
      <p className="mt-4 max-w-2xl" style={{ color: "var(--color-muted)" }}>
        {th.subtitle}
      </p>

      <div className="mt-16 space-y-6">
        {/* Planner */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={inView ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: 0.4 }}
          className="p-5 rounded-xl text-center max-w-sm mx-auto"
          style={{
            background: "var(--color-bg-surface)",
            border: "1px solid rgba(255,255,255,0.2)",
          }}
        >
          <span style={{ color: "var(--color-text)" }}>{th.plannerLabel}</span>
          <div className="text-xs mt-1" style={{ color: "var(--color-muted)" }}>
            {th.plannerSub}
          </div>
        </motion.div>

        {/* Layers */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {LAYERS.map((l, i) => (
            <motion.div
              key={l.id}
              initial={{ opacity: 0, y: 16 }}
              animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
              transition={{ delay: 0.3 + i * 0.15, duration: 0.4 }}
              className="p-5 rounded-xl text-center"
              style={{
                background: "var(--color-bg-surface)",
                border: `1px solid ${l.color}`,
              }}
            >
              <div className="font-medium" style={{ color: l.color }}>
                Layer {l.id}
              </div>
              <div className="text-xs mt-1" style={{ color: "var(--color-muted)" }}>
                agent: {l.agent}
              </div>
              <div className="mt-3 text-xs" style={{ color: "rgba(255,255,255,0.4)" }}>
                {th.layerSub}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Aggregator */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={inView ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.95 }}
          transition={{ delay: 1.0, duration: 0.5 }}
          className="p-6 rounded-xl text-center max-w-sm mx-auto"
          style={{ border: "1px solid var(--color-accent)" }}
        >
          <div className="font-medium" style={{ color: "var(--color-accent)" }}>
            {th.aggregatorLabel}
          </div>
          <div className="text-xs mt-1" style={{ color: "var(--color-muted)" }}>
            {th.aggregatorSub}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
