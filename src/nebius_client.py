import os
import httpx
import json
import re
from typing import Any

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")
_env_base = os.getenv("NEBIUS_API_BASE", "https://api.tokenfactory.nebius.com/v1")
NEBIUS_URL = f"{_env_base.rstrip('/')}/chat/completions"
NEBIUS_MODEL = "meta-llama/Llama-3.3-70B-Instruct"

def map_value_to_prompt(val: float, low_desc: str, high_desc: str) -> str:
    if val < 0.2: return f"Extreme focus on {low_desc}."
    if val < 0.4: return f"Prefer {low_desc}."
    if val < 0.6: return f"Balanced between {low_desc} and {high_desc}."
    if val < 0.8: return f"Prefer {high_desc}."
    return f"Extreme focus on {high_desc}."

async def smart_grade_answer(task: Any) -> dict:
    if not NEBIUS_API_KEY:
        return {"error": "Missing API Key"}

    strictness_ins = map_value_to_prompt(task.strictness, "semantic essence and core concept", "strict technical terminology and formal rigor")
    tone_ins = map_value_to_prompt(task.tone, "constructive and supportive coaching", "rigorous and sharp academic criticism")
    audience_ins = map_value_to_prompt(task.audience, "layman terms and simple analogies", "advanced professional depth and complex synthesis")
    focus_ins = f"Core Evaluation Focus: {', '.join(task.focus_areas)}."

    rubric_str = "\n".join([f"- Criteria: {p.text}" for p in task.reference_answers])

    prompt = f"""
    [CRITICAL CONSTRAINT: ADAPTIVE GRADING]
    - CURRENT STRICTNESS: {task.strictness} / 1.0
    - IF Strictness Level is HIGH (e.g., 'strict technical terminology'): Penalize heavily for using 'common words' instead of scientific terms. 
    - IF Strictness Level is LOW (semantic essence): You MUST award 1.0 if the student understands the general idea, even if they use "layman terms" or skip specific component names.
    - DO NOT penalize for missing technical jargon unless Strictness is HIGH.
    - NO GHOST CRITICISM: Do NOT suggest using a term if the student has ALREADY used it in their answer.
    - IF Tone is 'rigorous academic criticism': Be blunt and point out every minor error.
    - IF Audience is 'advanced professional': Do not give credit for superficial explanations.
    
    [Context]
    Subject Domain: {task.subject}
    Required Strictness: {strictness_ins}  <-- YOU MUST STRICTLY FOLLOW THIS SCALE
    Target Tone: {tone_ins}

    [Input Data]
    Question: {task.question}
    Rubric Points:
    {rubric_str}
    Student Answer: "{task.purple_answer}"

    [Task 1: Dialectical Evaluation]
    For EACH rubric point, perform the following internal debate:
    1. THESIS: Does the student mention the core concept? (Yes/No + Evidence)
    2. ANTITHESIS: Evaluate accuracy vs. the {task.strictness} strictness. Is there a REAL logical flaw, or just a lack of jargon? (Only penalize jargon if Strictness > 0.7)
    3. SYNTHESIS: Final decision. If the idea is correct and Strictness is LOW, the coefficient MUST be 1.0.

    [Task 2: Adaptive Planning]
    Based on the gaps identified in the evaluation, generate a brief, personalized study plan.

    [Output Constraints]
    - Return ONLY valid JSON.
    - Coefficient MUST be 0.0 (Miss), 0.5 (Partial), or 1.0 (Full).
    - score_coefficient: Must reflect the Synthesis verdict.

    [JSON Schema]
    {{
      "breakdown": [
        {{
          "rubric_point": "text",
          "evidence_found": "quote from student",
          "score_coefficient": 0.0, 
          "status": "match/partial/missed",
          "reflexion_log": "**THESIS:** ...\\n**ANTITHESIS:** ...\\n**SYNTHESIS:** ...",
          "comment": "Feedback in {tone_ins} style. If strictness is low, be encouraging."
        }}
      ],
      "overall_feedback": "High level summary.",
      "study_plan": {{
         "identified_gap": "Main weakness identified",
         "recommended_focus": "Specific topic to review",
         "action_item": "One concrete exercise or reading suggestion"
      }}
    }}
    """

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            payload = {
                "model": NEBIUS_MODEL,
                "messages": [
                    {"role": "system", "content": "You are an advanced AI Grading Agent utilizing Thesis-Antithesis-Synthesis logic. You output strictly structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3, 
                "max_tokens": 1500,
                "response_format": {"type": "json_object"}
            }
            
            headers = {
                "Authorization": f"Bearer {NEBIUS_API_KEY}",
                "Content-Type": "application/json"
            }

            response = await client.post(NEBIUS_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            raw_content = data["choices"][0]["message"]["content"]
            
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            return json.loads(raw_content)
            
    except Exception as e:
        return {"error": f"Model Inference Error: {str(e)}"}