from pydantic import BaseModel, Field
from typing import List


class SceneInteractionAndTrigger(BaseModel):
    intentions: List[str] = Field(description="The intentions of the scene. The number of intentions is 3.")
#   action: str = Field(description="The action of the scene.")
#   ending: str = Field(description="The ending of the scene.")
#   story: str = Field(description="The story of the scene.")