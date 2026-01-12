# AgentX Green Agent: Dialectical TAS Evaluator

This repository contains the advanced automated QA Assessor for the **AgentBeats** competition. Unlike traditional scorers, this agent employs a **Multi-Agent Dialectical Engine** to perform high-fidelity evaluation with human-like reasoning.

---

## 🚀 Key Innovation: TAS Logic
Our Green Agent doesn't just "check" answers; it **debates** them using the **Thesis-Antithesis-Synthesis (TAS)** framework for every rubric point:



* **Thesis (The Recognizer):** Identifies the presence of core concepts and extracts direct evidence from the student's response.
* **Antithesis (The Critic):** Challenges the answer for logical gaps, missing technical terminology, or vagueness based on the user-defined **Rigor Level**.
* **Synthesis (The Judge):** Reconciles the debate to produce a final score coefficient, ensuring fairness across different strictness settings.

---

## ✨ Core Features
* **Adaptive Rigor Control:** A dynamic slider (0.0 to 1.0) that shifts the engine from "Concept-First" (semantic matching) to "Technical-Rigor" (exact formal terminology).
* **Multi-Agent Reasoning:** Powered by **Llama-3.3-70B** via Nebius AI to simulate an internal academic debate for every assessment criterion.
* **Visual Evaluation Dashboard:** A dedicated Streamlit UI to visualize the internal cognitive process, debate logs, and scoring breakdown.
* **Actionable Study Plans:** Generates personalized improvement steps by identifying the specific cognitive gaps in responses.

---

## 🛠 Project Structure
| File/Folder | Description |
| :--- | :--- |
| `app/` | Backend core (FastAPI implementation of the A2A protocol). |
| `streamlit_app.py` | Frontend interactive dashboard for visualization. |
| `docker-compose.yml` | Orchestration for one-click deployment of both services. |
| `agent_card.json` | Standardized metadata for AgentBeats Dashboard registration. |
| `requirements.txt` | Project dependencies. |
| `.env.example` | Template for environment variables. |

---

## 🚦 Getting Started

### Prerequisites
* **Docker** and **Docker Compose** installed.
* A valid **Nebius API Key**.

### Installation & Deployment

1.  **Clone the project** and navigate to the root directory.
2.  **Environment Setup**: Copy the example environment file and fill in your keys:
    ```bash
    cp .env.example .env
    ```
    Ensure `.env` contains:
    ```env
    NEBIUS_API_KEY=your_actual_api_key_here
    NEBIUS_API_BASE=[https://api.tokenfactory.nebius.com/v1](https://api.tokenfactory.nebius.com/v1)
    NEBIUS_MODEL=meta-llama/Llama-3.3-70B-Instruct
    ```
3.  **One-Click Launch**:
    ```bash
    docker-compose up --build
    ```



### Accessing the System
* **Frontend UI:** [http://localhost:8501](http://localhost:8501)
* **Backend API:** [http://localhost:8000](http://localhost:8000)

> **💡 Pro Tip:** In the Streamlit sidebar, the **Backend Endpoint** should be set to `http://backend:8000/evaluate` to allow the containers to communicate over the internal Docker network.

---

## 📡 API Specification
* **POST `/evaluate`**
    * **Input:** Standard `TaskInput` (question, reference_answers, purple_answer, strictness).
    * **Output:** Structured JSON including `score`, `awarded_score`, and `metadata` containing the **reflexion_log**.

---
**Developed for the AgentBeats Competition.**