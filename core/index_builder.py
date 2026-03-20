"""
NoRag Core — Index Builder.

Génère les 3 fichiers index Markdown :
1. index_agents.md   — Catalogue des agents/skills/system prompts
2. index_documents.md — Index documentaire détaillé
3. index_history.md   — Historique des conversations avec résumés
"""

from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class AgentInfo:
    """Description d'un agent/skill."""
    name: str
    description: str
    system_prompt_path: str = ""
    competences: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    models: list[str] = field(default_factory=lambda: ["Gemini", "Claude", "GPT-4", "Grok"])
    active: bool = True


@dataclass
class SessionSummary:
    """Résumé d'une session de conversation."""
    session_id: str
    date: str
    summary: str
    documents_consulted: list[str] = field(default_factory=list)
    exchange_count: int = 0


class IndexBuilder:
    """Génère les 3 fichiers index Markdown."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    # ── INDEX AGENTS ──────────────────────────────────────────────────────────

    def build_agents_index(
        self,
        agents: list[AgentInfo],
        output_path: Path | None = None,
    ) -> str:
        """Génère le contenu de index_agents.md."""
        lines = [
            "# 🤖 Index des Agents & Skills",
            "",
            f"*Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "## 📋 Vue d'ensemble",
            "",
            "| Agent | Domaine | Compétences | Activation |",
            "|-------|---------|-------------|------------|",
        ]

        for agent in agents:
            competences_str = ", ".join(agent.competences[:3])
            status = "✅ Actif" if agent.active else "⏸️ Inactif"
            lines.append(
                f"| {agent.name} | {agent.description[:50]} | {competences_str} | {status} |"
            )

        lines.append("")
        lines.append("---")
        lines.append("")

        for agent in agents:
            lines.extend(self._build_agent_block(agent))

        content = "\n".join(lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")

        return content

    def _build_agent_block(self, agent: AgentInfo) -> list[str]:
        """Génère le bloc Markdown d'un agent."""
        lines = [
            f"## 🔧 Agent : {agent.name}",
            f"- **Description** : {agent.description}",
        ]

        if agent.system_prompt_path:
            lines.append(f"- **System Prompt** : `{agent.system_prompt_path}`")

        if agent.competences:
            lines.append("- **Compétences** :")
            for comp in agent.competences:
                lines.append(f"  - {comp}")

        if agent.commands:
            lines.append(f"- **Commandes** : {', '.join(agent.commands)}")

        if agent.models:
            lines.append(f"- **Modèles supportés** : {', '.join(agent.models)}")

        lines.extend(["", "---", ""])
        return lines

    # ── INDEX DOCUMENTS ───────────────────────────────────────────────────────

    def build_documents_index(
        self,
        documents_md: str,
        output_path: Path | None = None,
    ) -> str:
        """
        Génère index_documents.md.
        
        Accepte un contenu Markdown déjà structuré (e.g. l'index existant)
        et l'enrichit avec un en-tête et des métadonnées.
        """
        # Compter les documents (lignes commençant par ## 📄)
        doc_count = sum(1 for line in documents_md.splitlines() if line.startswith("## 📄"))

        header = "\n".join([
            "# 📚 Index des Documents",
            "",
            f"*Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            f"*Documents indexés : {doc_count}*",
            "",
            "---",
            "",
        ])

        content = header + documents_md

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")

        return content

    # ── INDEX HISTORY ─────────────────────────────────────────────────────────

    def build_history_index(
        self,
        sessions: list[SessionSummary],
        output_path: Path | None = None,
    ) -> str:
        """Génère index_history.md."""
        # Statistiques
        total_sessions = len(sessions)
        total_exchanges = sum(s.exchange_count for s in sessions)
        last_activity = sessions[0].date if sessions else "aucune"

        # Compter les documents les plus consultés
        doc_freq: dict[str, int] = {}
        for s in sessions:
            for doc in s.documents_consulted:
                doc_freq[doc] = doc_freq.get(doc, 0) + 1
        top_docs = sorted(doc_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        top_docs_str = ", ".join(f"{doc} ({count}x)" for doc, count in top_docs)

        lines = [
            "# 📜 Index Historique des Conversations",
            "",
            f"*Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "## 📊 Statistiques",
            f"- Sessions totales : {total_sessions}",
            f"- Échanges totaux : {total_exchanges}",
            f"- Dernière activité : {last_activity}",
        ]

        if top_docs_str:
            lines.append(f"- Documents les plus consultés : {top_docs_str}")

        lines.extend(["", "---", ""])

        # Sessions (les plus récentes d'abord)
        for session in sessions:
            lines.extend([
                f"## 🗓️ Session: {session.session_id} ({session.date})",
                f"- **Résumé** : {session.summary}",
            ])
            if session.documents_consulted:
                lines.append(
                    f"- **Documents consultés** : {', '.join(session.documents_consulted)}"
                )
            lines.append(f"- **Nb échanges** : {session.exchange_count}")
            lines.append("")

        content = "\n".join(lines)

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")

        return content

    # ── UTILITAIRE : mise à jour incrémentale de l'historique ────────────────

    def append_session_to_history(
        self,
        history_path: Path,
        session: SessionSummary,
    ) -> None:
        """Ajoute une session au fichier index_history.md existant."""
        block = "\n".join([
            "",
            f"## 🗓️ Session: {session.session_id} ({session.date})",
            f"- **Résumé** : {session.summary}",
            f"- **Documents consultés** : {', '.join(session.documents_consulted)}",
            f"- **Nb échanges** : {session.exchange_count}",
            "",
        ])

        if history_path.exists():
            with history_path.open("a", encoding="utf-8") as f:
                f.write(block)
        else:
            # Créer le fichier avec l'en-tête
            header = "\n".join([
                "# 📜 Index Historique des Conversations",
                "",
                f"*Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
                "",
                "## 📊 Statistiques",
                "- Sessions totales : 1",
                "",
                "---",
            ])
            history_path.parent.mkdir(parents=True, exist_ok=True)
            history_path.write_text(header + block, encoding="utf-8")
