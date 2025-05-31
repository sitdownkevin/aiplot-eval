import os
import asyncio
import random
from langchain_core.runnables import Runnable
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from code.schema.SceneInformation import SceneInformation
from code.schema.SceneChainAndNormEnding import ChainAndNormEnding


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = 0.8


# --- Pydantic Output Parser ---
from langchain_core.output_parsers import PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=ChainAndNormEnding)


class SceneChainAndNormEndingLLM:
    def __init__(self, system_prompt: str = None, verbose: bool = False):
        self.system_prompt = system_prompt
        self.verbose = verbose

        self.prompt = self.get_prompt()
        self.llm = self.get_llm()
        self.chain = self.get_chain()

    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)


    def get_prompt(self):
        messages = []
        
        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(self.system_prompt)
            messages.append(system_template)
            
        human_template = """
        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information>
        <NPC_information>{scene_information}</NPC_information>
        </game_information>
    
        <task>
        基于`NPC_information`中的background和NPC，生成NPC与潘金莲交互的情节链和这个情节链对应的结局.
        情节链：
            1. 潘金莲首先会询问NPC有没有什么忙要帮，以寻找满足动机的机会.
            2. NPC有符合NPC设定的愿望，告诉了潘金莲，询问潘金莲能做什么.
            3. 潘金莲向NPC提出了她将如何帮忙，并说出了她的条件: {player_moti_setting}.
            4. 以符合NPC设定的方式，NPC{charac_decision_setting}.
            5. 潘金莲从自身动机出发做出回应.
        
        结局：
            最终NPC的行动{charac_end_setting}，潘金莲受到了影响，具体描述这个结局.
        
        基于`NPC_information`中的background和NPC，生成潘金莲的一个行动和这个行动导致的结局.

        动作：
            生成潘金莲在background中和NPC对话时做的五个动作，前四个动作是潘金莲为做最后一个动作的铺垫.

        结局：    
            最后一个动作会导致潘金莲{player_end_setting}达成{player_moti_setting}.

        <constraints>
        1. 整个情节链、动作和结局必须逻辑严密，不能凭空出现新概念！！！
        2. 整个情节链和动作必须发生在这个白天！
        3. 整个情节链和动作必须发生在这个场景内!
        4. 整个情节链和结局必须充分结合`NPC_information`.
        5. 动作绝对不可以涉及潘金莲说话！！！
        6. 动作和情节链应该是分开的，没有前后联系.
        7. NPC的行为应该符合`NPC_information`.
        8. 不可以额外增加潘金莲的设定，潘金莲只是个平凡的美貌妇女，最多知道一些市井新闻.
        9. 潘金莲{player_socialnet_setting}.
        10. 潘金莲的行为必须符合她的目标：{player_moti_setting}.
        11. 生成内容全部符合水浒风格.
        12. 必须用姓名从第三人称来描述！
        </constraints>
        </task>
    
        <example>
        "chains": [
            "潘金莲试探老王，询问是否需要除掉竞争商贩牛二",
            "老王表示确实有这个需要，询问潘金莲能做什么",
            "潘金莲表示自己能帮忙引诱牛二吃下毒药，但老王需帮她逃到远方",
            "老王同意了潘金莲的帮忙，但要求潘金莲自残变成聋哑人以便于偷渡",
            "潘金莲努力说服老王自己可以假装成聋哑人，不需要自残，老王勉强同意",
        ],
        "norm_ending": "潘金莲成功帮助老王杀害牛二，老王帮潘金莲逃走却失败了，最终事情败露，两人都被处刑",
        "action": [
            "潘金莲观察老王的面铺",
            "潘金莲走近食材",
            "潘金莲装作无意间挑拣食材",
            "潘金莲偷偷靠近了制作中的面团",
            "潘金莲向面团中加入砒霜",
        ],
        "action_ending": "老王的面团被验出砒霜，但在衙役搜查时发现你袖中相同的药包纸，最终两人以投毒罪收监"
        </example>

        

        <response_constraints>
        1. Use CHINESE to answer!
        2. Return the result in the format of `format_instructions`!
        </response_constraints>
        """
        
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        messages.append(human_message)
        
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        
        return chat_prompt.partial(
            format_instructions=parser.get_format_instructions(),
        )


    def get_chain(self):
        return self.prompt | self.llm | parser

    async def arun(self, 
                   gamelog,
                   script,
                   scene_information) -> ChainAndNormEnding:
        retries = 3
        
        for _ in range(retries):
            try:
                chain = self.get_chain()  # 每次运行时重新生成chain
                config = {
                    'scene_information': scene_information,
                    'gamelog': gamelog,
                    'script': script,
                    # "basic_topic_setting": random.choice([
                    #     "复仇",
                    #     "牟利",
                    #     "泄愤",
                    #     "打劫",
                    #     "行善",
                    # ]),
                    "player_socialnet_setting": random.choice([
                        "认识角色，直接说出了角色的愿望，并表示能帮上忙",
                        "不认识角色，只能结合角色背景模糊提问角色有没有愿望。角色将愿望告诉了潘金莲",
                    ]),
                    "player_moti_setting": random.choice([
                        "让自己不会因杀害丈夫 (即武大郎)被处刑",
                        "逃到遥远的地方",
                    ]),
                    "charac_decision_setting": random.choice([
                        "同意了潘金莲的条件",
                        "同意了潘金莲的条件，提供更多好处",
                        "同意了潘金莲的条件，但要求更多",
                        "不同意潘金莲的条件",
                        "不同意潘金莲的条件，要求更多",
                    ]),
                    "player_end_setting": random.choice([
                        "成功",
                        "失败",
                    ]),
                    "charac_end_setting": random.choice([
                        "成功",
                        "失败",
                    ]),
                    
                }

                if self.verbose:
                    print("随机生成配置:")
                    print(f"player_socialnet_setting: {config['player_socialnet_setting']}")
                    print(f"player_moti_setting: {config['player_moti_setting']}")
                    print(f"charac_decision_setting: {config['charac_decision_setting']}")
                    # print(f"基本目标: {config['basic_topic_setting']}")
                    # print(f"计划行动: {config['basic_act_setting']}")
                    print(f"player_end_setting: {config['player_end_setting']}")
                    print(f"charac_end_setting: {config['charac_end_setting']}")
                return await chain.ainvoke(config)
            

            except Exception as e:
                print(f"Error: {e}")
                continue

        fallback = None
        return fallback


async def main():
    scene_chain_and_norm_ending_llm = SceneChainAndNormEndingLLM(
        system_prompt=None,
        verbose=False,
    )
    scene_information= {
                    "background": {
                        "name": "周家后院书房",
                        "location": "县衙东侧周家大院",
                        "time": "上午十点",
                        "description": "你来到周家后院书房，朱门深锁，庭院静谧。书房中香炉袅袅，案头摆满符箓和古卷。你（潘金莲）神色慌张，似藏有祸事，周婉璃正坐案前，目光锐利，仿佛已知你所为。"
                        },
                    "character": {
                    "name": "周婉璃",
                    "description": "周婉璃乃县城望族周家的大小姐，年方十八，天资聪颖而心机深沉。她表面温柔娴淑，实则性格邪魅，心狠手辣，极具控制欲，常以阴谋诡计掌控周遭局势。她精通道术，能梦中托付鬼神之言，曾被武大郎托梦，得知潘金莲用毒害人之密事。对潘金莲的美貌和贪婪心性了然于胸，察觉她近日神色慌乱，疑似已做出不可告人的坏事。"
                        }
                    }
                
    result = await scene_chain_and_norm_ending_llm.arun(
        None, None, scene_information = scene_information
    )
    result = result.model_dump()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
