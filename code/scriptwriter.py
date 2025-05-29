import asyncio
from abc import ABC, abstractmethod
from code.config import Config
from code.llm import LLMProvider
from code.gai.SceneInformation import SceneInformationLLM
from code.gai.SceneChainAndNormEnding import SceneChainAndNormEndingLLM
from code.gai.SceneStreamByChain import SceneStreamByChainLLM
from code.gai.SceneInteractionAndTrigger import SceneInteractionAndTriggerLLM


class BaseScriptwriterAgent(ABC):
    def __init__(
        self,
        llm_model=Config.DRAMA_AGENT_MODEL_NAME,
        llm_provider=Config.DRAMA_AGENT_MODEL_PROVIDER,
    ):
        self._llm_model = llm_model
        self._llm_provider = LLMProvider(provider=llm_provider)

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
    def __init__(self,
                 llm_model=Config.DRAMA_AGENT_MODEL_NAME,
                 llm_provider=Config.DRAMA_AGENT_MODEL_PROVIDER,
                 ):
        super().__init__(llm_model, llm_provider)

        verbose = True

        self.scene_information_llm = SceneInformationLLM(
            system_prompt=None, verbose=verbose)
        self.scene_chain_and_norm_ending_llm = SceneChainAndNormEndingLLM(
            system_prompt=None, verbose=verbose)
        self.scene_stream_by_chain_llm = SceneStreamByChainLLM(
            system_prompt=None)
        self.scene_interaction_and_trigger_llm = SceneInteractionAndTriggerLLM(
            system_prompt=None)

    async def gen_new_scene_script(self, script=None, gamelog=None):
        output_scene_name = None
        output_scene_description = None
        output_scene_character = None
        output_scene_plot_chain = []
        output_scene_stream = {}
        output_scene_interaction_conversation = []
        output_scene_interaction_action = []
        output_scene_trigger = {}
        output_scene_endings = {}

        # 生成信息
        # 生成场景信息
        scene_information = await self.scene_information_llm.arun(gamelog=gamelog, script=script)
        scene_information = scene_information.model_dump()
        # 生成情节链和结局
        scene_chain_and_norm_ending = await self.scene_chain_and_norm_ending_llm.arun(gamelog=gamelog, script=script, scene_information=scene_information)
        scene_chain_and_norm_ending = scene_chain_and_norm_ending.model_dump()

        # 添加 action_ending
        output_scene_interaction_action.append(
            f"{scene_chain_and_norm_ending['action']}$2")
        output_scene_endings[f'结局{18+len(output_scene_endings)}'] = {
            "流": scene_chain_and_norm_ending["action_ending"],
        }
        output_scene_trigger[f"{scene_chain_and_norm_ending['action']}$2"] = {
            "跳转": list(output_scene_endings.keys())[-1],
        }

        # 添加 norm_ending
        output_scene_endings[f'结局{18+len(output_scene_endings)}'] = {
            "流": scene_chain_and_norm_ending["norm_ending"],
        }

        # 生成流
        chain_todo = scene_chain_and_norm_ending["chains"] + \
            [scene_chain_and_norm_ending["norm_ending"]]
        tasks = []
        for i in range(len(chain_todo)-1):
            tasks.append(self.scene_stream_by_chain_llm.arun(gamelog=gamelog,
                                                             script=script,
                                                             scene_information=scene_information,
                                                             scene_chain=chain_todo[i],
                                                             next_scene_chain=chain_todo[i+1]))
        scene_stream_by_chain = await asyncio.gather(*tasks)
        scene_stream_by_chain = [v.model_dump() for v in scene_stream_by_chain]

        tasks_scene_interaction_and_trigger = []
        label_scene_interaction_and_trigger = []
        label_key_hint_scene_interaction_and_trigger = []
        history_rounds = []
        last_scene_name = None
        for scene_stream, scene in zip(scene_stream_by_chain, chain_todo[:-1]):
            # 填充剧本
            stream = []
            for i, round in enumerate(scene_stream["rounds"]):
                # 填充剧本
                # if i == 0: stream.append(f"关键提示: {round['key_hint']}")
                if i == 0:
                    stream.append({
                        "关键提示": round["key_hint"],
                    })
                stream.append(f"NPC TALK: {round['npc_talk']}")
                stream.append(f"ROLE TALK: {round['role_talk']}")

                # 基于 round 生成交互，构建 tasks_scene_interaction_and_trigger
                tasks_scene_interaction_and_trigger.append(
                    self.scene_interaction_and_trigger_llm.arun(
                        gamelog=gamelog,
                        script=script,
                        history_rounds=history_rounds,
                        current_round=round,
                    )
                )
                label_scene_interaction_and_trigger.append(last_scene_name)
                label_key_hint_scene_interaction_and_trigger.append(
                    round["key_hint"])
                history_rounds.append(round)

            # 填充剧本
            output_scene_stream[scene] = stream
            last_scene_name = scene

        results_scene_interaction_and_trigger = await asyncio.gather(*tasks_scene_interaction_and_trigger)
        results_scene_interaction_and_trigger = [
            v.model_dump() for v in results_scene_interaction_and_trigger]

        label_key_hint_scene_interaction_and_trigger = label_key_hint_scene_interaction_and_trigger[1:] + [
            None]
        count_intention = 0
        for result, label, key_hint in zip(results_scene_interaction_and_trigger, label_scene_interaction_and_trigger, label_key_hint_scene_interaction_and_trigger):
            # 添加当前 round 的交互语义
            data = []
            for i, intention in enumerate(result["intentions"]):
                data.append(
                    f'{intention}$语义{count_intention}{f" ({label})" if label else ""}')

                if key_hint:
                    output_scene_trigger[f"{intention}$语义{count_intention}"] = {
                        "关键提示": key_hint,
                    }
                else:
                    output_scene_trigger[f"{intention}$语义{count_intention}"] = {
                        "跳转": list(output_scene_endings.keys())[-1],
                    }

                count_intention += 1

            output_scene_interaction_conversation.extend(data)

        # 填充剧本
        output_scene_name = scene_information["background"]["name"]
        output_scene_description = f"地点：{scene_information['background']['location']}\\n时间：{scene_information['background']['time']}\\n{scene_information['background']['description']}"
        output_scene_character = f"{scene_information['character']['name']}。{scene_information['character']['description']}"
        output_scene_plot_chain = scene_chain_and_norm_ending["chains"]

        output = {
            output_scene_name: {
                "场景": output_scene_description,
                "人物": output_scene_character,
                "情节链": output_scene_plot_chain,
                "流": output_scene_stream,
                "交互": {
                    "对话": output_scene_interaction_conversation,
                    "动作选择": output_scene_interaction_action,
                },
                "触发": output_scene_trigger,
            },
        }

        for k, v in output_scene_endings.items():
            output[k] = v

        return output

    def fake(self):
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


async def main():
    scriptwriter_agent = ScriptwriterAgent()
    result = await scriptwriter_agent.gen_new_scene_script()

    import json
    print('----------- `gen_new_scene_script` result -----------')
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
