"use client";
import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { useLang } from "@/lib/i18n";

function Box({
  label,
  subtitle,
  color,
  active,
  delay,
}: {
  label: string;
  subtitle?: string;
  color: string;
  active: boolean;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={active ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
      transition={{ delay, duration: 0.4 }}
      className="p-5 rounded-xl text-center"
      style={{
        background: "var(--color-bg-surface)",
        border: `1px solid ${color}`,
      }}
    >
      <div className="font-medium" style={{ color }}>
        {label}
      </div>
      {subtitle && (
        <div className="text-xs mt-1" style={{ color: "var(--color-muted)" }}>
          {subtitle}
        </div>
      )}
    </motion.div>
  );
}

function Arrow({ active, delay }: { active: boolean; delay: number }) {
  return (
    <motion.div
      initial={{ scaleX: 0 }}
      animate={active ? { scaleX: 1 } : { scaleX: 0 }}
      transition={{ delay, duration: 0.3 }}
      className="h-px origin-left hidden md:block"
      style={{ background: "rgba(255,255,255,0.25)", width: "4rem" }}
    />
  );
}

export function L1Demo() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: false, margin: "-30% 0px" });
  const { t } = useLang();
  const th = t.l1Demo;

  return (
    <section id="l1" ref={ref} className="py-32 px-6 max-w-5xl mx-auto scroll-mt-20">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        {th.title}{" "}
        <span style={{ color: "var(--color-muted)" }}>{th.titleSub}</span>
      </h2>
      <p className="mt-4 max-w-2xl" style={{ color: "var(--color-muted)" }}>
        {th.subtitle}
      </p>

      <div className="mt-16 flex flex-col md:flex-row items-center gap-4 md:gap-0">
        <Box label="Question" color="#ffffff" active={inView} delay={0} />
        <Arrow active={inView} delay={0.3} />
        <Box
          label="Router (SLM)"
          subtitle="→ agent + docs"
          color="var(--color-accent)"
          active={inView}
          delay={0.5}
        />
        <Arrow active={inView} delay={0.9} />
        <Box
          label="Answer (LLM)"
          subtitle="[doc_id, section]"
          color="var(--color-accent-2)"
          active={inView}
          delay={1.1}
        />
      </div>

      <motion.pre
        initial={{ opacity: 0 }}
        animate={inView ? { opacity: 1 } : { opacity: 0 }}
        transition={{ delay: 1.5, duration: 0.5 }}
        className="mt-12 p-6 rounded-xl text-sm overflow-x-auto max-w-full"
        style={{
          background: "var(--color-bg-surface)",
          border: "1px solid rgba(255,255,255,0.1)",
        }}
      >{`{
  "agent_id": "juriste_conformite",
  "documents": [
    { "doc_id": "contrat_acme", "sections": ["art_7", "annexe_A"] }
  ],
  "reasoning": "Contract retention question → juriste + SLA clauses"
}`}</motion.pre>
    </section>
  );
}
