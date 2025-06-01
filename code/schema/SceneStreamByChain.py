from pydantic import BaseModel, Field
from typing import List


class Round(BaseModel):
    key_hint: str = Field(description="The key hint of the scene.")
    npc_talk: str = Field(description="The talk of the conversation for NPC. Example: 老王：你袖口沾的可是石灰？今早西巷棺材铺刚运走三袋。")
    role_talk: str = Field(description="The talk of the conversation for 潘金莲. Example: 潘金莲：我，我……")


class SceneStreamByChain(BaseModel):
    rounds: List[Round] = Field(description="The round of the scene. The round of the conversation is 1.")