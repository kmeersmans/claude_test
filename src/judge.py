"""Core judge orchestrator — ties PDF reading, LLM calls, and score storage together."""

import json
import re
from pathlib import Path

from src.config_loader import load_criteria, load_llm_config
from src.llm.base import LLMProvider
from src.llm.ollama_provider import OllamaProvider
from src.llm.bedrock_provider import BedrockProvider
from src.pdf_reader import extract_text
from src.prompt_builder import build_system_prompt, build_user_prompt
from src.score_store import save_scores


def _create_provider() -> tuple[LLMProvider, str]:
    """Instantiate the active LLM provider based on config.

    Returns:
        (provider_instance, model_identifier_string)
    """
    cfg = load_llm_config()

    if cfg.active_provider == "ollama":
        oc = cfg.ollama
        provider = OllamaProvider(
            model=oc.model,
            base_url=oc.base_url,
            temperature=oc.temperature,
            num_ctx=oc.num_ctx,
        )
        return provider, f"ollama/{oc.model}"

    if cfg.active_provider == "bedrock":
        bc = cfg.bedrock
        provider = BedrockProvider(
            model_id=bc.model_id,
            region=bc.region,
            temperature=bc.temperature,
            max_tokens=bc.max_tokens,
            profile=bc.profile,
        )
        return provider, f"bedrock/{bc.model_id}"

    raise ValueError(f"Unknown provider: {cfg.active_provider}")


def _parse_llm_response(raw: str) -> list[dict]:
    """Extract the evaluations JSON array from the LLM response.

    Handles cases where the model wraps JSON in markdown code fences.
    """
    # Try to find a JSON block in code fences first
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    json_str = fence_match.group(1) if fence_match else raw

    # Find the outermost { ... }
    brace_match = re.search(r"\{.*\}", json_str, re.DOTALL)
    if not brace_match:
        raise ValueError(f"Could not find JSON in LLM response:\n{raw}")

    parsed = json.loads(brace_match.group(0))
    return parsed["evaluations"]


def judge_document(pdf_path: Path) -> dict:
    """Run the full LLM judge pipeline on a single PDF.

    Steps:
        1. Load config and criteria.
        2. Extract text from the PDF.
        3. Build prompts and call the LLM.
        4. Parse the structured response.
        5. Persist scores.

    Args:
        pdf_path: Path to the PDF to evaluate.

    Returns:
        Dict with keys: document, model, evaluations.
    """
    criteria_cfg = load_criteria()
    llm_cfg = load_llm_config()

    # 1. Extract text
    text = extract_text(pdf_path)
    document_name = pdf_path.name

    # 2. Build prompts
    system_prompt = build_system_prompt(llm_cfg.system_preamble, criteria_cfg)
    user_prompt = build_user_prompt(text, document_name)

    # 3. Call LLM
    provider, model_id = _create_provider()
    raw_response = provider.generate(system_prompt, user_prompt)

    # 4. Parse response
    evaluations = _parse_llm_response(raw_response)

    # 5. Persist scores
    save_scores(
        judge_type="llm",
        user_id=model_id,
        document=document_name,
        evaluations=evaluations,
    )

    return {
        "document": document_name,
        "model": model_id,
        "evaluations": evaluations,
        "raw_response": raw_response,
    }
