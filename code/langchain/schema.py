from typing import List, Dict, TypedDict, Optional

class ScriptSchema(TypedDict):
    ...


class GamelogSchema(TypedDict):
    plot_history: List[str]
    clue_history: List[str]
    hint_history: List[str]
    interaction_history: List[str]


class NextSceneInformationSchema(TypedDict):
    scene_name: str
    scene_location: str
    scene_time: str
    scene_description: str
    character_name: str
    character_description: str
    

class NextSceneStreamAndNormEndingSchema(TypedDict):
    stream_a: str
    stream_b: str
    stream_c: str
    stream_d: str
    stream_e: Optional[str]
    stream_f: Optional[str]
    ending: str