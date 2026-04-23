"use client";
import { motion } from "framer-motion";

export function Hero() {
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
        Two explicit pipelines. Markdown indexes you can read. Full sections fed
        to the model. Citations you can audit.
      </motion.p>

      <div className="mt-12 flex gap-4">
        <a
          href="/blueprint-en.html"
          className="px-6 py-3 rounded-full font-medium hover:opacity-90 transition"
          style={{ background: "var(--color-accent)", color: "#fff" }}
        >
          Read the blueprint
        </a>
        <a
          href="https://github.com/supergmax/NoRag"
          className="px-6 py-3 rounded-full border hover:border-white/40 transition"
          style={{ borderColor: "rgba(255,255,255,0.15)" }}
        >
          GitHub
        </a>
      </div>
    </section>
  );
}
