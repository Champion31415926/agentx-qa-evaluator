from app.utils import normalize_text
from app.nebius_client import smart_grade_answer
from typing import Any
import math

async def score_answer(task: Any) -> dict:
    student_answer = task.purple_answer
    reference_answers = task.reference_answers
    
    total_max = sum(r.max_score for r in reference_answers)
    norm_student = normalize_text(student_answer)
    
    if not norm_student:
        return {
            "score": 0.0, "awarded_score": 0.0, "max_score": total_max,
            "reason": "empty_answer", "feedback": "No content provided.", 
            "breakdown": [],
            "study_plan": {}
        }

    grading_result = await smart_grade_answer(task)
    
    if "error" in grading_result:
        return {
            "score": 0.0, "awarded_score": 0.0, "max_score": total_max,
            "reason": "ai_error", "feedback": grading_result["error"], 
            "breakdown": [],
            "study_plan": {}
        }

    ai_breakdown = grading_result.get("breakdown", [])
    study_plan = grading_result.get("study_plan", {})
    
    final_awarded = 0.0
    final_breakdown = []

    for idx, ref in enumerate(reference_answers):
        ai_item = ai_breakdown[idx] if idx < len(ai_breakdown) else {}
        
        try:
            raw_coeff = float(ai_item.get("score_coefficient", 0.0))
        except:
            raw_coeff = 0.0
            
        if raw_coeff >= 0.75: 
            coeff = 1.0
        elif raw_coeff >= 0.25: 
            coeff = 0.5
        else: 
            coeff = 0.0
            
        weight = ref.max_score
        
        if coeff == 1.0:
            item_awarded = weight
        elif coeff == 0.5:
            # 计算原始的一半得分
            raw_half = weight * 0.5
            # 使用 round(x * 2) / 2 的技巧将结果修约为 0.5 的倍数
            item_awarded = float(round(raw_half * 2) / 2)
        else:
            item_awarded = 0.0
            
        final_awarded += item_awarded
        
        final_breakdown.append({
            "rubric_point": ref.text,
            "evidence_found": ai_item.get("evidence_found", ""),
            "coefficient_score": coeff,
            "status": "match" if coeff == 1.0 else ("partial" if coeff == 0.5 else "missed"),
            "comment": ai_item.get("comment", ""),
            "reflexion_log": ai_item.get("reflexion_log", ""),
            "max_score": weight,
            "awarded_score": item_awarded
        })

    return {
        "score": (final_awarded / total_max) if total_max > 0 else 0.0,
        "awarded_score": final_awarded,
        "max_score": total_max,
        "reason": "graded",
        "feedback": grading_result.get("overall_feedback", "Grading complete."),
        "breakdown": final_breakdown,
        "study_plan": study_plan
    }