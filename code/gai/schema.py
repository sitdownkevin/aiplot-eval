from typing import List, Dict, TypedDict, Optional

class ScriptSchema(TypedDict):
    ...


class GamelogSchema(TypedDict):
    plot_history: List[str]
    clue_history: List[str]
    hint_history: List[str]
    interaction_history: List[str]

'''
生成场景和人物信息
'''
class SceneInformationSchema(TypedDict):
    scene_name: str
    scene_location: str
    scene_time: str
    scene_description: str
    character_name: str
    character_description: str
    

'''
生成情节链。固定SceneChain数量为5, 有一个正常ENDING, 其余为drama.py自动添加的 $1离开 -> 跳转场景大街，不设置其他跳转。
因为支线人物并不存在于主线故事中，若跳回场景将回到主线，可能总会降低评分（支线总与上下文无关，叙事连贯性有限）。
注意：变量名大小写被调整。
'''
class SceneChainAndNormEndingSchema(TypedDict):
    CHAIN_A: str
    CHAIN_B: str
    CHAIN_C: str
    CHAIN_D: str
    CHAIN_E: str
    ENDING: str

# before
# class SceneChainAndNormEndingSchema(TypedDict):
#     CHAIN_A: str
#     chain_b: str
#     chain_c: str
#     CHAIN_D: str
#     CHAIN_E: Optional[str]
#     CHAIN_F: Optional[str]
#     ENDING: str
    
'''
生成流。固定为一个Stream包括两轮对话，TO<charac>: XXX, <charac>: XXX 算一轮。
（可以固定起手是什么，例如TO<charac>或<charac>，即<潘金莲>先说话或是<charac>先说话）。

在生成Stream每一轮内容时，即可生成KEY_HINT_ROUND1和KEY_HINT_ROUND2，效果是：提供潘金莲动机，辅助<潘金莲>说出符合流的对话，用于后续生成对话意图，和对应触发。
每个Stream的标题 (即Chain) 作为KEY_CLUE，用于后续作为对话和动作选择的出现条件，控制它们可被选择的时机。

CAUTION!!!
1. 若"关键提示"在Stream的首行，则会在流开始时被读入，用于指导生成预设回复，KEY_HINT_ROUND1必须保持其在首行，至关重要！（若不在，则流结束才读入）
2. KEY_HINT_ROUND2不需要在最终输出的"流"中出现，只被用于传入后续SceneInteractionAndTrigger，最终在"触发"中呈现。
2. 当且仅当：当前Stream被判定结束时，当前Stream的KEY_CLUE才被记录。因此约束对话或动作选择仅出现在流2的条件是：流1标题且not其他标题。
CAUTION!!!
'''

class SceneStreamByChainSchema(TypedDict):
    KEY_HINT_ROUND1: str
    KEY_HINT_ROUND2: str # 用于后续处理，生成但最终不呈现在流中
    TALK_A1: str
    TALK_B1: str
    TALK_A2: str
    TALK_B2: str
    KEY_CLUE: str

# before
# class SceneStreamByChainSchema(TypedDict):
#     TALK_A1: str
#     TALK_B1: str
#     TALK_A2: Optional[str]
#     TALK_B2: Optional[str]
#     TALK_A3: Optional[str]
#     TALK_B3: Optional[str]
#     KEY_HINT: Optional[str]
#     KEY_CLUE: Optional[str]

'''
无须在"触发"中生成关键线索，output文件夹中gamelog并不会保留记录。
因为关键线索只能被用于（）中的出现条件，所有"触发"中的关键线索都可以直接被替换为对应的语义或动作选择。

60%进行对话，40%概率进行动作，进行动作时，20%选$1离开，如果没有其他动作，就100%选$1离开，$1离开是自动添加的。因此，最好有一些动作选择，避免过多随机选择$1离开。

###对话连贯性机制设计前提：
对每个chain，都会通过关键提示，选择最相关的talk_intention生成若干个prereply（预设选项）。LLM会选择其中一项
若talk_intention小于等于2，就会生成talk_intention为"玩家流露出继续当前剧情的意图"，因此，每次都应该提供三个对话意图供选择。

### 对话连贯性机制设计：
1. 每个流的开始会提供"关键提示"KEY_HINT_ROUND1，用于第一轮对话提示。第一轮对话提示会命中语义1或2或3（通过出现条件约束，每个流里有且仅有3个对话选择，例如：仅出现在流2的条件是：流1标题且not其他标题。），全都触发，得到下一个"关键提示"KEY_HINT_ROUND2，用于第二轮对话提示。依此类推。
2. 因此，5个流共10轮，每轮3个对话意图$语义，共有30个对话意图$语义。每3个大致类似，都对应当轮对话。这些对话意图$语义作用于触发，用于补充流中的"关键提示"KEY_HINT_ROUND2，引导流中的第二轮对话。因此，对话用的触发有30个，标题是对话意图，下一级内容是"关键提示"KEY_HINT_ROUND1（实际生效会被流中KEY_HINT_ROUND1覆盖，仅维持格式规范）和KEY_HINT_ROUND2，"关键提示"从Stream中获取。
3. 最后一轮对话的3个对话意图$语义，均触发跳转至结局ENDING。
4. 流程：
    LLM处理：遍历Stream中的每一轮，基于Stream中的每一轮和对应的KEY_HINT_ROUND1/2，生成三个大致含义相同的对话意图$语义。
    代码处理：
        a. 将生成的对话意图$语义，依次和KEY_HINT_ROUND1/2以及ENDING组合为触发。
        b. 对话意图$语义后加（），限制其出现的轮数，通过Stream的KEY_CLUE（即Stream的标题，Chain）组合进行约束。

### 动作选择机制设计前提：    
动作会随机触发，高度不可控，为确保动作不影响连贯性，建议选择动作将直接导致触发新结局。

### 动作选择机制设计：
1. 对每个Stream，生成1个可能的动作选择，并生成这个动作选择将导致的结局，5个动作选择依次对应ENDING_ACTION_1-5。
2. 动作选择$后加（），限制其出现的轮数，通过Stream的KEY_CLUE（即Stream的标题，Chain）组合进行约束。
3. 将生成的动作选择$，依次和ENDING_ACTION_1-5组合为触发。
'''
class SceneInteractionAndTrigger(TypedDict):
    # TALK_INTENTION_1到30
    TALK_INTENTION_STREAM1_ROUND1_1: str
    TALK_INTENTION_STREAM1_ROUND1_2: str
    TALK_INTENTION_STREAM1_ROUND1_3: str
    # ...（可以换个别的名字，例如直接1-30，反正语义也是$语义1-30）
    # (后续组合括号内条件，限定对话意图出现的流位置)

    # 对话意图$语义 1-30 对应的 触发 1-30
    TRIGGER_TALK_1: str
    # TRIGGER_1到30（后续和Stream里的KEY_HINT_ROUND1/2组合即可构成完整输出，每三个都一样）
    # 例如：让郓哥离开$语义2:
    #        关键提示: 要不要找王婆或者西门庆商量呢？
    # ...

    # 动作选择$ 1-5
    ACTION_1: str
    # ...
    # (后续组合括号内条件，限定动作选择出现的流位置)

    # 动作选择$ 1-5 对应的 触发 1-5 & 对应的Ending 1-5
    TRRIGGER_ACTION_1: str
    ENDING_ACTION_1: str
    # ...（后续组合三者构成完整触发）
    # 例如：殴打郓哥$2:
    #        跳转: 结局18
    # 结局18:
    #   流: 被击毙
    # ...