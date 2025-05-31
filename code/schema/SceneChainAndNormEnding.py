from pydantic import BaseModel, Field
from typing import List


class ChainAndNormEnding(BaseModel):
    chains: List[str] = Field(description="The chain of the scene. The number of chains is 5.")
    norm_ending: str = Field(description="The norm ending of the scene.")
    action: List[str] = Field(description="The action of the scene. The number of actions is 5.")
    action_ending: str = Field(description="The action ending of the scene.")