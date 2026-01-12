from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import TaskInput, EvaluationResult
from app.scorer import score_answer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/evaluate", response_model=EvaluationResult)
async def evaluate(task: TaskInput):
    try:
        result = await score_answer(task)
        return EvaluationResult(
            task_id=task.task_id,
            score=result["score"],
            awarded_score=result["awarded_score"],
            max_score=result["max_score"],
            metadata={
                "feedback": result.get("feedback"),
                "breakdown": result.get("breakdown", []),
                "study_plan": result.get("study_plan", {})
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))