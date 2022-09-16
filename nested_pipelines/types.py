from pydantic import BaseModel
from typing import Optional, TypeVar

T = TypeVar("T", bound=BaseModel)


class PipelineStatus(BaseModel):
    id: str
    status: Optional[str]

    @property
    def complete(self) -> bool:
        return self.status is not None and self.status.lower() in [
            "error",
            "failed",
            "skipped",
            "succeeded",
        ]

    @property
    def success(self) -> bool:
        return self.status is not None and self.status.lower() in [
            "skipped",
            "succeeded",
        ]
