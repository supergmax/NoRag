import { highlight } from "@/lib/highlight";

const INDEX_SAMPLE = `## contrat_saas_acme
- **Titre** : Contrat SaaS — Acme Technologies
- **Résumé** : Accord B2B SaaS couvrant SLA, rétention des données, et sécurité.
- **Sections** :
  - \`art_7\` — Rétention données — mots-clés : rétention, RGPD, purge, 90 jours
  - \`annexe_A\` — SLA et disponibilité — mots-clés : SLA, uptime, 99.9%, crédit`;

const AGENTS_SAMPLE = `## juriste_conformite
**Description** : expert juridique B2B (contrats, RGPD, SLA).
**Quand l'utiliser** : clauses, rétention, DPA, SLA.
**System prompt** :
> Tu es juriste senior. Tu cites [doc_id, section] systématiquement.`;

export async function UnderTheHood() {
  const [indexHtml, agentsHtml] = await Promise.all([
    highlight(INDEX_SAMPLE, "markdown"),
    highlight(AGENTS_SAMPLE, "markdown"),
  ]);

  return (
    <section className="py-32 px-6 max-w-5xl mx-auto">
      <h2 className="text-4xl md:text-5xl font-semibold tracking-tight">
        Under the hood.
      </h2>
      <p className="mt-4 max-w-2xl" style={{ color: "var(--color-muted)" }}>
        Two Markdown files. That&apos;s the entire &ldquo;database&rdquo;. Git-diffable,
        human-readable, zero infra.
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
