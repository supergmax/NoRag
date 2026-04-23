"use client";
import { useLang } from "@/lib/i18n";

export function Footer() {
  const { t } = useLang();

  return (
    <footer
      className="py-16 px-6 text-sm"
      style={{
        borderTop: "1px solid rgba(255,255,255,0.05)",
        color: "var(--color-muted)",
      }}
    >
      <div className="max-w-5xl mx-auto flex items-center justify-between flex-wrap gap-4">
        <span>{t.footer}</span>
        <a
          href="https://github.com/supergmax/NoRag"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-white transition-colors"
        >
          github.com/supergmax/NoRag
        </a>
      </div>
    </footer>
  );
}
