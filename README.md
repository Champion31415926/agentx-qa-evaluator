# AgentX Green Agent: Dialectical TAS Evaluator

This repository contains the advanced automated QA Assessor for the **AgentBeats** competition. Unlike traditional keyword-matching scorers, this agent employs a **Multi-Agent Dialectical Engine** to perform high-fidelity evaluation with human-like reasoning.

---

## 🚀 Key Innovation: TAS Logic

Our Green Agent doesn't just "check" answers; it **debates** them using the **Thesis-Antithesis-Synthesis (TAS)** framework for every rubric point:

* **Thesis (The Recognizer):** Identifies the presence of core concepts and extracts direct evidence from the student's response.
* **Antithesis (The Critic):** Challenges the answer for logical gaps, missing technical terminology, or vagueness based on the user-defined **Rigor Level**.
* **Synthesis (The Judge):** Reconciles the debate to produce a final score coefficient, ensuring fairness across different strictness settings.

---

## ✨ Core Features

* **A2A Protocol Compliant:** Fully supports the Agent-to-Agent protocol, including automatic discovery via `/.well-known/agent-card.json`.
* **Adaptive Rigor Control:** A dynamic strictness parameter that shifts the engine from "Semantic Essence" (concept matching) to "Formal Rigor" (exact technical terminology).
* **Multi-Agent Reasoning:** Powered by **Llama-3.3-70B** (via Nebius AI) to simulate an internal academic debate for every assessment criterion.
* **Actionable Insights:** Provides a structured `reflexion_log` and personalized improvement steps by identifying specific cognitive gaps.

---

## 🛠 Project Structure

```text
.
├── src/
│   ├── agent.py          # Core A2A logic & TAS entry point
│   ├── server.py         # A2A Server setup & Agent Card configuration
│   ├── scorer.py         # TAS Dialectical logic implementation
│   ├── nebius_client.py  # Nebius LLM API client
│   ├── models.py         # Pydantic data models
│   └── ...               # A2A utilities (executor, messenger, etc.)
├── tests/
│   └── test_agent.py     # Automated A2A conformance tests
├── .github/workflows/    # CI/CD (Test, Build, and Publish to GHCR)
├── Dockerfile            # uv-based high-performance container config
└── pyproject.toml        # Modern Python dependency management

```

---

## 🚦 Getting Started

### 1. Prerequisites

* [uv](https://docs.astral.sh/uv/) installed (recommended) or Docker.
* A valid **Nebius API Key**.

### 2. Local Development

Create a `.env` file in the root directory:

```env
NEBIUS_API_KEY=your_actual_api_key_here
NEBIUS_API_BASE=https://api.tokenfactory.nebius.com/v1
NEBIUS_MODEL=meta-llama/Llama-3.3-70B-Instruct

```

Start the A2A service:

```bash
uv run src/server.py --port 9009

```

### 3. CI/CD & Deployment

This project is configured with GitHub Actions. When you push to the `main` branch:

1. **Test:** Automatically runs `pytest` to verify A2A protocol compatibility.
2. **Build:** Packages the agent into a Docker image.
3. **Publish:** Pushes the image to **GitHub Container Registry (GHCR)**.

**Image URL:** `ghcr.io/<your-username>/<repo-name>:latest`

---

## 📡 API Specification (A2A)

* **GET `/.well-known/agent-card.json**`: Retrieve the agent's capabilities and metadata.
* **POST `/v1/tasks**`: Submit an evaluation task.
* **Input:** A2A Message containing `TaskInput` (question, reference_answers, purple_answer).
* **Output:** Structured JSON including `score`, `awarded_score`, and `metadata` containing the **reflexion_log**.



---

**Developed for the AgentBeats Competition.**
