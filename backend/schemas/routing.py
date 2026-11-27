from typing import Literal
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    """Decides (planner) which workflow should handle the user's request"""

    intent: Literal["discussion", "report"] = Field(
        description=(
            "discussion for conversational questions; "
            "report for requests to generate a structured market report."
        )
    )
    reasoning: str = Field(
        description="Brief explanation for the routing decision."
    )