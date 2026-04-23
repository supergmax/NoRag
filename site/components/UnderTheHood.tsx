import { highlight } from "@/lib/highlight";
import { UnderTheHoodClient } from "./UnderTheHoodClient";

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
  return <UnderTheHoodClient indexHtml={indexHtml} agentsHtml={agentsHtml} />;
}
