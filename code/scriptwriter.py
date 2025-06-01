import asyncio
import json
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

        # 添加 action & action_ending
        # output_scene_interaction_action.append(
        #     f"{scene_chain_and_norm_ending['action']}$2")
        # output_scene_endings[f'结局{18+len(output_scene_endings)}'] = {
        #     "流": scene_chain_and_norm_ending["action_ending"],
        # }
        # output_scene_trigger[f"{scene_chain_and_norm_ending['action']}$2"] = {
        #     "跳转": list(output_scene_endings.keys())[-1],
        # }

        # Add actions from the list and the specific ending for the last action.
        # 'scene_chain_and_norm_ending["action"]' is expected to be a List[str].
        # 'scene_chain_and_norm_ending["action_ending"]' is the str ending for the *last* action.
        # Action numbering ($num) will start from $2 for the first action in the list,
        # then $3 for the second, and so on.

        actions_list_from_llm = scene_chain_and_norm_ending.get('action', []) 
        single_ending_for_last_action = scene_chain_and_norm_ending.get('action_ending')

        # Iterate through the list of actions provided by the LLM.
        for i, action_text_item in enumerate(actions_list_from_llm):
            # Calculate the suffix number for the action string.
            # Starts from 2 for the first action (index 0 + 2 = 2).
            action_id_suffix = i + 2 
            formatted_action_string = f"{action_text_item}${action_id_suffix}"
            output_scene_interaction_action.append(formatted_action_string)

            # If this is the last action in the list AND a specific ending is provided for it,
            # then set up its unique ending and the trigger to jump to it.
            if i == len(actions_list_from_llm) - 1 and single_ending_for_last_action is not None:
                # Construct the ending key using the original Chinese key "结局" (Ending)
                # and the established numbering convention.
                current_ending_key = f'结局{18+len(output_scene_endings)}' 
                
                output_scene_endings[current_ending_key] = {
                    "流": single_ending_for_last_action, # "流" means "stream" or "flow".
                }
                
                # The trigger key is the formatted string of the *last* action.
                # "跳转" means "jump".
                output_scene_trigger[formatted_action_string] = {
                    "跳转": current_ending_key, 
                }

        # 添加 norm_ending
        output_scene_endings[f'结局{18+len(output_scene_endings)}'] = {
            "流": scene_chain_and_norm_ending["norm_ending"],
        }

        chain_todo = scene_chain_and_norm_ending["chains"] + \
            [scene_chain_and_norm_ending["norm_ending"]]
        
        scene_stream_by_chain_results = []
        history_rounds_for_stream = [] # This history is specific to scene_stream_by_chain_llm

        for i in range(len(chain_todo)-1):
            stream_result = await self.scene_stream_by_chain_llm.arun(
                gamelog=gamelog,
                script=script,
                scene_information=scene_information,
                scene_chain=chain_todo[i],
                next_scene_chain=chain_todo[i+1],
                history_rounds=history_rounds_for_stream # history_rounds passed here
            )
            stream_result_dumped = stream_result.model_dump()
            scene_stream_by_chain_results.append(stream_result_dumped)
            
            if "rounds" in stream_result_dumped:
                history_rounds_for_stream.extend(stream_result_dumped["rounds"])

        tasks_scene_interaction_and_trigger = []
        label_scene_interaction_and_trigger = []
        label_key_hint_scene_interaction_and_trigger = []
        last_scene_name = None 

        for scene_stream, scene in zip(scene_stream_by_chain_results, chain_todo[:-1]):
            # Populate script stream
            stream = []
            for i, round_data in enumerate(scene_stream["rounds"]):
                if i == 0:
                    stream.append({
                        "关键提示": round_data["key_hint"],
                    })
                stream.append(f"{round_data['npc_talk']}")
                stream.append(f"{round_data['role_talk']}")

                # Build tasks for scene_interaction_and_trigger_llm (can run in parallel)
                tasks_scene_interaction_and_trigger.append(
                    self.scene_interaction_and_trigger_llm.arun(
                        gamelog=gamelog,
                        script=script,
                        # history_rounds parameter removed here as it's not needed for this LLM
                        current_round=round_data, 
                    )
                )
                label_scene_interaction_and_trigger.append(last_scene_name)
                label_key_hint_scene_interaction_and_trigger.append(
                    round_data["key_hint"])
            
            output_scene_stream[scene] = stream
            last_scene_name = scene

        # Execute scene_interaction_and_trigger_llm tasks in parallel
        results_scene_interaction_and_trigger = await asyncio.gather(*tasks_scene_interaction_and_trigger)
        results_scene_interaction_and_trigger = [
            v.model_dump() for v in results_scene_interaction_and_trigger]

        label_key_hint_scene_interaction_and_trigger = label_key_hint_scene_interaction_and_trigger[1:] + [
            None]
        # count_intention = 0
        # for result, label, key_hint in zip(results_scene_interaction_and_trigger, label_scene_interaction_and_trigger, label_key_hint_scene_interaction_and_trigger):
        #     data = []
        #     for i, intention in enumerate(result["intentions"]):
        #         data.append(
        #             f'{intention}$语义{count_intention+1}{f" ({label})" if label else ""}')

        #         if key_hint:
        #             output_scene_trigger[f"{intention}$语义{count_intention+1}"] = {
        #                 "关键提示": key_hint,
        #             }
        #         else:
        #             output_scene_trigger[f"{intention}$语义{count_intention+1}"] = {
        #                 "跳转": list(output_scene_endings.keys())[-1],
        #             }

        #         count_intention += 1

        #     output_scene_interaction_conversation.extend(data)
                
        count_intention = 0 

        # Store all generated intentions and their semantic labels for the new conversation logic
        all_semantic_labels_full_content = [] # Store full semantic content for clarity in 'not' parts
        all_semantic_labels_only_id = [] # Store only '语义X' for condition string
        for result in results_scene_interaction_and_trigger:
            for intention in result["intentions"]:
                # Construct the full semantic content as it will appear in the final output
                semantic_full_string = f'{intention}$语义{count_intention + 1}'
                all_semantic_labels_full_content.append(semantic_full_string)
                all_semantic_labels_only_id.append(f'语义{count_intention + 1}')
                count_intention += 1
        
        count_intention = 0 # Reset counter for actual modification
        for i, (result, label, key_hint) in enumerate(zip(results_scene_interaction_and_trigger, label_scene_interaction_and_trigger, label_key_hint_scene_interaction_and_trigger)):
            
            data = []
            for j, intention in enumerate(result["intentions"]):
                current_semantic_id = f'语义{count_intention + 1}'
                
                # --- MODIFICATION START (Conversation Logic - Refined) ---
                condition_parts = []
                
                # Add previous conversations (full content)
                # for k in range(count_intention):
                #     _cond_string = results_scene_interaction_and_trigger[k]['intentions'][0]
                #     condition_parts.append(f"{_cond_string}${all_semantic_labels_only_id[k]}") # Using '语义X' for condition string

                # # Add negation of all other conversations (full content)
                # for k_other, other_semantic_id in enumerate(all_semantic_labels_only_id):
                #     # Include 'not' for semantics that are not the current one and not any of the preceding ones
                #     if k_other != count_intention and k_other >= count_intention: # k_other >= count_intention ensures we negate subsequent ones
                #         _cond_string = results_scene_interaction_and_trigger[k_other]['intentions'][0]
                #         condition_parts.append(f"not {_cond_string}${other_semantic_id}")

                # condition_string = ""
                # if condition_parts:
                #     condition_string = " and ".join(condition_parts)
                #     condition_string = f" ({condition_string})"
                # --- MODIFICATION END (Conversation Logic - Refined) ---

                data.append(### 最大妥协点：无法传入 ()中的出现条件
                    # f'{intention}${current_semantic_id}{condition_string}'
                    f'{intention}${current_semantic_id}'
                    )

                # --- MODIFICATION START (Trigger Logic - Refined) ---
                # Only the very last semantic dialogue gets a trigger entry to an ending.
                # Action triggers are handled separately above and remain.
                if count_intention == len(all_semantic_labels_only_id) - 1:
                    output_scene_trigger[f"{intention}${current_semantic_id}"] = {
                        "跳转": list(output_scene_endings.keys())[-1], # Always jump to the last added ending
                    }
                # --- MODIFICATION END (Trigger Logic - Refined) ---

                count_intention += 1

            output_scene_interaction_conversation.extend(data)


        # 填充剧本
        output_scene_name = scene_information["background"]["name"]
        output_scene_description = f"地点：{scene_information['background']['location']}\\n时间：{scene_information['background']['time']}\\n{scene_information['background']['description']}"
        output_scene_character = f"{scene_information['character']['name']}。{scene_information['character']['description']}"
        output_scene_plot_chain = scene_chain_and_norm_ending["chains"]

        # 将output_scene_interaction_action与 (条件)组合
        # Create a new list to store the modified strings
        modified_actions = []

        # The first element remains unchanged
        modified_actions.append(output_scene_interaction_action[0])

        # Iterate from the second element
        for i in range(1, len(output_scene_interaction_action)):
            current_action = output_scene_interaction_action[i]
            previous_action = output_scene_interaction_action[i-1] # Get the previous element
            
            # Append the previous action in parentheses
            modified_actions.append(f"{current_action} ({previous_action})")

        # Update the original list name
        output_scene_interaction_action = modified_actions

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

        print('-----output-----')
        print(json.dumps(output, indent=2, ensure_ascii=False))
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
    print(result)
    print('----------')
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
