"use client";
import { motion } from "framer-motion";
import { useLang } from "@/lib/i18n";

export function Hero() {
  const { t } = useLang();
  const th = t.hero;

  return (
    <section className="relative isolate min-h-[90vh] flex flex-col items-center justify-center px-6">
      <motion.h1
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="text-6xl md:text-8xl font-semibold tracking-tight text-center"
      >
        NoRag.
        <br />
        <span style={{ color: "var(--color-accent)" }}>RAG without vectors.</span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
        className="mt-8 max-w-xl text-center text-lg"
        style={{ color: "var(--color-muted)" }}
      >
        {th.subtitle}
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.6 }}
        className="mt-12 flex gap-4"
      >
        <a
          href="/blueprint"
          className="px-6 py-3 rounded-full font-medium hover:opacity-90 transition"
          style={{ background: "var(--color-accent)", color: "#fff" }}
        >
          {th.cta1}
        </a>
        <a
          href="https://github.com/supergmax/NoRag"
          target="_blank"
          rel="noopener noreferrer"
          className="px-6 py-3 rounded-full border hover:border-white/40 transition"
          style={{ borderColor: "rgba(255,255,255,0.15)" }}
        >
          {th.cta2}
        </a>
      </motion.div>
    </section>
  );
}
