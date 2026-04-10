# LLM Judge

Evaluate PDF documents using LLMs (Ollama or Amazon Bedrock) and/or human reviewers via a Streamlit web app. Evaluation criteria are fully configurable through YAML — no code changes needed to adjust what gets scored.

## Project structure

```
├── config/
│   ├── criteria.yaml        # Evaluation criteria — edit this to change what gets judged
│   └── llm_config.yaml      # LLM provider settings and system prompt
├── input/                   # Drop PDF files here
├── output/                  # Optional JSON output from CLI
├── scores/                  # SQLite database (auto-created)
├── src/
│   ├── config_loader.py     # YAML → Pydantic models
│   ├── pdf_reader.py        # PDF text extraction
│   ├── prompt_builder.py    # Builds LLM prompts from criteria config
│   ├── judge.py             # Orchestrator: PDF → LLM → scores DB
│   ├── score_store.py       # SQLite storage for all scores
│   └── llm/
│       ├── base.py          # Abstract LLM provider interface
│       ├── ollama_provider.py
│       └── bedrock_provider.py
├── app.py                   # Streamlit human judge UI
├── run_judge.py             # CLI entry point for LLM judge
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

### Ollama (local)

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3.1:8b`
3. Ensure `config/llm_config.yaml` has `active_provider: "ollama"`

### Amazon Bedrock

1. Configure AWS credentials (`aws configure` or environment variables)
2. Set `active_provider: "bedrock"` in `config/llm_config.yaml`
3. Adjust `model_id` and `region` as needed

## Usage

### LLM Judge (CLI)

```bash
# Place PDFs in the input/ folder, then:

# Judge a single PDF
python run_judge.py input/my_paper.pdf

# Judge all PDFs in input/
python run_judge.py --all

# Override provider for a single run
python run_judge.py --provider bedrock input/my_paper.pdf

# Save results to JSON
python run_judge.py --all --output output/results.json
```

### Human Judge (Streamlit)

```bash
streamlit run app.py
```

1. Enter your User ID in the sidebar
2. Select a PDF from the dropdown
3. Score each criterion on a 1–5 scale
4. Submit — scores are saved to the SQLite database

The **Review Scores** tab shows all recorded scores (LLM and human), with filters by document and judge type.

## Customising evaluation criteria

Edit `config/criteria.yaml`. Each criterion has:

| Field         | Purpose                                             |
|---------------|-----------------------------------------------------|
| `id`          | Unique key used in storage and LLM JSON output      |
| `name`        | Display name                                        |
| `description` | What to evaluate (shown to LLM and human judges)    |
| `scale_min/max` | Score range                                       |
| `guidelines`  | Per-score descriptions for consistent grading       |

Adding or removing a criterion in the YAML automatically updates both the LLM prompt and the Streamlit UI.

## Future extensions

The YAML config has commented-out sections for:

- **Hard rules** — automated checks (word count, plagiarism thresholds) that flag or reject documents before scoring
- **Additional context** — source materials or rubric notes injected into the LLM prompt for richer evaluation
