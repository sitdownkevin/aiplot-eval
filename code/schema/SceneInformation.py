from pydantic import BaseModel, Field
from typing import List

class SceneBackground(BaseModel):
    name: str = Field(description="The name of the scene. Example: 老王烧饼铺.")
    location: str = Field(description="The location of the scene. Example: 老王烧饼铺.")
    time: str = Field(description="The time of the scene. Example: 上午十点.")
    description: str = Field(description="The description of the scene. Example: 你来到隔壁老王的烧饼铺，蒸笼冒着热气却未见武大郎的摊位.")

class SceneCharacter(BaseModel):
    name: str = Field(description="The name of the character. Example: 老王.")
    description: str = Field(description="The description of the character. Example: 隔壁老王四十余岁，满脸横肉，手臂有烫伤疤痕。因摊位纠纷与武大郎积怨已久，近日正在争夺早市黄金摊位.")

class SceneInformation(BaseModel):
    background: SceneBackground = Field(description="The background of the scene.")
    character: SceneCharacter = Field(description="The character of the scene.")