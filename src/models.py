from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ReferenceAnswer(BaseModel):
    text: str = Field(..., description="Description of Evaluation Criteria")
    max_score: float = Field(..., description="This point is awarded full marks")

class TaskInput(BaseModel):
    task_id: str
    question: str
    reference_answers: List[ReferenceAnswer]
    purple_answer: str
    subject: str = "General"
    strictness: float = 0.5
    tone: float = 0.5
    audience: float = 0.5
    focus_areas: List[str] = ["accuracy"]

class EvaluationResult(BaseModel):
    task_id: str
    score: float 
    awarded_score: float 
    max_score: float 
    metadata: Dict[str, Any]