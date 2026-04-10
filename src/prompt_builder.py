"""Build LLM prompts from the criteria configuration.

This module translates config/criteria.yaml into the system and user prompts
sent to the LLM. To change evaluation behaviour, edit criteria.yaml or the
system_preamble in llm_config.yaml — you should rarely need to touch this file.
"""

from src.config_loader import CriteriaConfig, Criterion


def build_system_prompt(preamble: str, criteria: CriteriaConfig) -> str:
    """Construct the full system prompt.

    Combines the free-form preamble (persona, output format) with
    auto-generated criterion descriptions so they stay in sync with the config.
    """
    sections = [preamble.strip(), "", "## Evaluation Criteria", ""]

    for c in criteria.criteria:
        sections.append(f"### {c.name} (id: {c.id})")
        sections.append(f"Scale: {c.scale_min}–{c.scale_max}")
        sections.append(c.description.strip())
        sections.append("")
        sections.append("Score guidelines:")
        for score in sorted(c.guidelines):
            sections.append(f"  {score}: {c.guidelines[score]}")
        sections.append("")

    return "\n".join(sections)


def build_user_prompt(text: str, document_name: str) -> str:
    """Wrap the extracted PDF text in a clear user-level prompt."""
    return (
        f"Please evaluate the following document (\"{document_name}\") "
        f"according to ALL the criteria described in your instructions.\n\n"
        f"---BEGIN DOCUMENT---\n{text}\n---END DOCUMENT---"
    )


def format_criterion_for_display(c: Criterion) -> str:
    """Render a single criterion as human-readable text (used in Streamlit)."""
    lines = [f"**{c.name}**", c.description.strip(), ""]
    for score in sorted(c.guidelines):
        lines.append(f"- **{score}**: {c.guidelines[score]}")
    return "\n".join(lines)
