from typing import List, Dict, TypedDict, Optional

class ScriptSchema(TypedDict):
    ...


class GamelogSchema(TypedDict):
    plot_history: List[str]
    clue_history: List[str]
    hint_history: List[str]
    interaction_history: List[str]


class SceneInformationSchema(TypedDict):
    scene_name: str
    scene_location: str
    scene_time: str
    scene_description: str
    character_name: str
    character_description: str
    

class SceneChainAndNormEndingSchema(TypedDict):
    CHAIN_A: str
    chain_b: str
    chain_c: str
    CHAIN_D: str
    CHAIN_E: Optional[str]
    CHAIN_F: Optional[str]
    ENDING: str
    

class SceneStreamByChainSchema(TypedDict):
    TALK_A1: str
    TALK_B1: str
    TALK_A2: Optional[str]
    TALK_B2: Optional[str]
    TALK_A3: Optional[str]
    TALK_B3: Optional[str]
    KEY_TIP: Optional[str]
    KEY_CLUE: Optional[str]