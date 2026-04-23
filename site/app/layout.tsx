import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NoRag — RAG without vectors",
  description:
    "Document Q&A without vector embeddings. LLM-driven routing over Markdown indexes. Two pipelines: L1 and Multi_L.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
