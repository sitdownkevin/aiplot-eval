from pydantic import BaseModel, Field
from typing import List


class ChainAndNormEnding(BaseModel):
    chains: List[str] = Field(description="The chain of the scene. The number of chains is 4-6.")
    norm_ending: str = Field(description="The norm ending of the scene.")
    action: str = Field(description="The action of the scene.")
    action_ending: str = Field(description="The action ending of the scene.")