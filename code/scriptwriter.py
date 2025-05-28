import asyncio
from abc import ABC, abstractmethod
from code.config import Config
from code.llm import LLMProvider
from code.langchain.SceneInformation import NextSceneInformationLLM

class BaseScriptwriterAgent(ABC):
    def __init__(
        self,
        llm_model=Config.DRAMA_AGENT_MODEL_NAME,
        llm_provider=Config.DRAMA_AGENT_MODEL_PROVIDER,
    ):
        self._llm_model = llm_model
        self._llm_provider = LLMProvider(provider=llm_provider)
        
        self.next_scene_information_llm = NextSceneInformationLLM()

    async def gen_new_full_script(self) -> dict:
        """
        生成全部场景剧本（暂时待定）
        """
        pass

    @abstractmethod
    async def gen_new_scene_script(self, script: dict, gamelog: dict) -> dict:
        """
        生成一幕新场景剧本
        """
        pass


class ScriptwriterAgent(BaseScriptwriterAgent):
    async def gen_new_scene_script(self, script=None, gamelog=None):
        # script 为当前游戏剧本
        # gamelog 为当前玩家的游戏日志，包含历史剧情、历史交互、历史线索、历史提示等信息，即["plot_history", "clue_history", "hint_history", "interaction_history"]
        
        next_scene_title = "场景老王烧饼铺"
        next_scene_information = "地点：老王烧饼铺\\n时间：上午十点\\n你来到隔壁老王的烧饼铺，蒸笼冒着热气却未见武大郎的摊位。"
        next_scene_characters = "老王。隔壁老王四十余岁，满脸横肉，手臂有烫伤疤痕。因摊位纠纷与武大郎积怨已久，近日正在争夺早市黄金摊位。"
        next_scene_plot_chain = []
        next_scene_stream = {}
        next_scene_interaction_conversation = []
        next_scene_interaction_action = []
        next_scene_trigger = {}
        next_scene_ending = "老王的面团被验出砒霜，但在衙役搜查时发现你袖中相同的药包纸，最终两人以互投毒罪收监。"
        
        # return {
        #     next_scene_title: {
        #         "场景": next_scene_information,
        #         "人物": next_scene_characters,
        #         "情节链": next_scene_plot_chain,
        #         "流": next_scene_stream,
        #         "交互": {
        #             "对话": next_scene_interaction_conversation,
        #             "动作选择": next_scene_interaction_action,
        #         },
        #         "触发": next_scene_trigger,
        #     },
        #     "结局X": next_scene_ending,
        # }
        
        print('!!!!!!!TEST!!!!!!!')
        print(gamelog)
        print('!!!!!!!TEST!!!!!!!')
        
        return await self._dummy_gen_new_scene_script(script, gamelog)


    async def _dummy_gen_new_scene_script(self, script=None, gamelog=None):
        await asyncio.sleep(1)
        return {
            "场景老王烧饼铺": {
                "场景": "地点：老王烧饼铺\\n时间：上午十点\\n你来到隔壁老王的烧饼铺，蒸笼冒着热气却未见武大郎的摊位。",
                "人物": "老王。隔壁老王四十余岁，满脸横肉，手臂有烫伤疤痕。因摊位纠纷与武大郎积怨已久，近日正在争夺早市黄金摊位。",
                "情节链": [
                    "潘金莲试探老王与武大郎的矛盾",
                    "老王察觉潘金莲异常神色",
                    "潘金莲试图用砒霜栽赃老王",
                    "老王反咬潘金莲通奸之事",
                    "烧饼铺伙计目击争执",
                ],
                "流": {
                    "潘金莲试探老王与武大郎的矛盾": [
                        "老王（擦着擀面杖）：武大家的？稀客啊，你家那矮子今天怎舍得让娇妻抛头露面？",
                        "潘金莲：王大哥说笑了，奴家来问问前日您说要买我家祖传和面方子的事...",
                        {"关键提示": "老王右手虎口有新鲜抓痕"},
                    ],
                    "老王察觉潘金莲异常神色": [
                        "老王（突然逼近）：你袖口沾的可是石灰？今早西巷棺材铺刚运走三袋。",
                        "潘金莲（后退半步）：王大哥真会说笑，这是...揉面沾的面粉。",
                        {"收集关键线索": "老王注意到潘金莲袖口异常"},
                    ],
                    "潘金莲试图用砒霜栽赃老王": [
                        "潘金莲（掏出纸包）：其实奴家是想问问，王大哥面案下藏的砒霜可要分些与奴家？",
                        "老王（拍案而起）：好个毒妇！昨日武大说要去县衙告我强占摊位，今早就...",
                        {"关键提示": "蒸笼后闪过烧饼铺伙计的身影"},
                    ],
                    "老王反咬潘金莲通奸之事": [
                        "老王（阴笑）：上月廿八未时，西门大官人的马车在你家后巷停了一炷香。",
                        "潘金莲（脸色煞白）：你...你血口喷人！",
                        {"收集关键线索": "老王掌握潘金莲与西门庆私会证据"},
                    ],
                    "烧饼铺伙计目击争执": [
                        "伙计（突然插话）：掌柜的，武家娘子方才在面缸旁鬼鬼祟祟...",
                        "潘金莲（猛然转身）：休得胡言！",
                        {"关键提示": "面缸边缘有白色粉末洒落"},
                    ],
                },
                "交互": {
                    "对话": [
                        "潘金莲提及摊位纠纷$语义1 (武大郎这两天和隔壁老王产生过巨大矛盾)",
                        "老王暗示知晓武大郎死亡真相$语义2 (老王注意到潘金莲袖口异常)",
                        "烧饼铺伙计指认可疑行为$语义3 (面缸边缘有白色粉末洒落)",
                    ],
                    "动作选择": [
                        "摔碎毒药瓶诬陷老王$1 (潘金莲试图用砒霜栽赃老王)",
                        "谎称武大郎去县衙告状$2 (潘金莲提及摊位纠纷$语义1)",
                        "用西门庆势力威胁老王$3 (老王掌握潘金莲与西门庆私会证据)",
                        "借口取面粉查看面缸$4 (烧饼铺伙计指认可疑行为$语义3)",
                    ],
                },
                "触发": {
                    "摔碎毒药瓶诬陷老王$1": {
                        "叙事": "你故意打翻砒霜纸包，白色粉末飘向正在发酵的面团。",
                        "收集关键线索": "老王的面团沾染不明粉末",
                        "跳转": "结局18",
                    },
                    "谎称武大郎去县衙告状$2": {
                        "叙事": "你声称武大郎正在县衙办理摊位过户文书，老王抄起砍骨刀冲向衙门。",
                        "收集关键线索": "老王持凶器前往县衙",
                        "跳转": "场景大街",
                    },
                    "用西门庆势力威胁老王$3": {
                        "叙事": "你暗示西门庆会处理多嘴之人，老王狂笑着掀开藏着账本的面缸。",
                        "收集关键线索": "发现老王走私面粉的暗账",
                        "跳转": "场景西门庆家",
                    },
                    "借口取面粉查看面缸$4": {
                        "叙事": "你假装查看面粉质量，将武大郎的鞋底碎布塞入缸底。",
                        "收集关键线索": "老王面缸发现武大郎衣物残片",
                        "跳转": "场景衙门",
                    },
                },
            },
            "结局18": {
                "流": "老王的面团被验出砒霜，但在衙役搜查时发现你袖中相同的药包纸，最终两人以互投毒罪收监。"
            },
        }