import json
from typing import Any
from pydantic import BaseModel, HttpUrl
from a2a.server.tasks import TaskUpdater
from a2a.types import Message, TaskState, Part, TextPart, DataPart
from a2a.utils import get_message_text, new_agent_text_message
from src.messenger import Messenger
from src.models import TaskInput
from src.scorer import score_answer

class EvalRequest(BaseModel):
    participants: dict[str, HttpUrl]
    config: dict[str, Any]

class Agent:
    required_roles: list[str] = ["purple_agent"]
    required_config_keys: list[str] = ["task_id", "question", "reference_answers"]

    def __init__(self):
        self.messenger = Messenger()

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        missing_roles = set(self.required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"
        missing_config_keys = set(self.required_config_keys) - set(request.config.keys())
        if missing_config_keys:
            return False, f"Missing config keys: {missing_config_keys}"
        return True, "ok"

    async def run(self, message: Message, updater: TaskUpdater) -> None:
        input_text = get_message_text(message)
        
        try:
            raw_data = json.loads(input_text)
            eval_req = EvalRequest(**raw_data)
            
            ok, msg = self.validate_request(eval_req)
            if not ok:
                await updater.reject(new_agent_text_message(msg))
                return
        except Exception as e:
            await updater.reject(new_agent_text_message(f"Request structural error: {e}"))
            return

        try:
            await updater.update_status(
                TaskState.working, new_agent_text_message("Calling Purple Agent for answer...")
            )
            
            purple_url = str(eval_req.participants["purple_agent"])
            question = eval_req.config["question"]
            
            question_msg = new_agent_text_message(question)
            purple_response_msg = await self.messenger.talk_to_agent(question_msg, purple_url)
            purple_answer = get_message_text(purple_response_msg)
            
            if not purple_answer:
                raise ValueError("Purple Agent returned an empty answer.")

            task_data = eval_req.config.copy()
            task_data["purple_answer"] = purple_answer
            
            task = TaskInput(**task_data)
            
            await updater.update_status(
                TaskState.working, new_agent_text_message("Evaluating using TAS Logic...")
            )

            result = await score_answer(task)
            
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=f"Final Score: {result.get('score', 0.0)}")),
                    Part(root=DataPart(data=result))
                ],
                name="Evaluation Result",
            )
            await updater.complete()
            
        except Exception as e:
            await updater.failed(new_agent_text_message(f"Execution error: {str(e)}"))