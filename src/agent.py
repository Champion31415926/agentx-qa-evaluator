import json
from typing import Any
from pydantic import BaseModel, HttpUrl, ValidationError
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
    required_roles: list[str] = []
    required_config_keys: list[str] = []

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
            data = json.loads(input_text)
            task = TaskInput(**data)
        except Exception as e:
            await updater.reject(new_agent_text_message(f"Invalid input: {e}"))
            return

        await updater.update_status(
            TaskState.working, new_agent_text_message("Evaluating using TAS Logic...")
        )

        try:
            result = await score_answer(task)
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=f"Score: {result['score']}")),
                    Part(root=DataPart(data=result))
                ],
                name="Evaluation Result",
            )
            await updater.complete()
        except Exception as e:
            await updater.failed(new_agent_text_message(f"Execution error: {e}"))