import os
import asyncio
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
import random
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = 0.8


from code.schema.SceneStreamByChain import SceneStreamByChain
from langchain_core.output_parsers import PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=SceneStreamByChain)


class SceneStreamByChainLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        
        self.prompt = self.get_prompt()
        self.llm = self.get_llm()
        self.chain = self.get_chain()

    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)

    def get_prompt(self):
        messages = []

        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(
                self.system_prompt)
            messages.append(system_template)

        human_template = """
        <format_instructions>{format_instructions}</format_instructions>
        
        <game_information>
        <gamelog>{gamelog}</gamelog>
        <script>{script}</script>
        <current_scene_information>{scene_information}</current_scene_information>
        <current_scene_chain>{scene_chain}</current_scene_chain>
        <next_scene_chain>{next_scene_chain}</next_scene_chain>
        </game_information>
    
        <task>
        <goal>
        基于`current_scene_chain`, 生成2轮符合`current_scene_information`的生动的对话，衔接到`next_scene_chain`.
        每轮对话包括：
            1. key_hint: 从潘金莲视角出发，描述她说话的动机.
            2. npc_talk: `scene_information`中的角色发言.
            3. role_talk: 潘金莲发言.
        </goal>
        <constraints>
        1. key_hint必须体现当轮潘金莲说话前的思考. 
        2. npc_talk和role_talk都以"人名：对话内容"的形式呈现.
        3. 必须充分遵循`current_scene_information`和`current_scene_chain`的设定.
        </constraints>
        </task>

        <example>
            "key_hint": "和王婆商量",
            "npc_talk": "王婆：金莲，什么事情上门呀？",
            "role_talk": "潘金莲：王婆，我想和你商量一点事。"
        </example>

        <response_constraints>
        1. Use CHINESE to answer!
        2. Return the result in the format of `format_instructions`!
        </response_constraints>
        """

        human_message = HumanMessagePromptTemplate.from_template(
            human_template)
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
                   scene_information: str,
                   scene_chain: str,
                   next_scene_chain: str) -> SceneStreamByChain:
        retries = 3

        for _ in range(retries):
            try:
                return await self.get_chain().ainvoke({
                    "gamelog": gamelog,
                    "script": script,
                    "scene_information": {
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
                    },
                    "scene_chain": "潘金莲提出帮周婉璃设计计谋，助其除去祸害，但条件是周婉璃必须帮她安排逃往遥远的地方。",
                    "next_scene_chain": "周婉璃眼神一凛，冷声拒绝潘金莲的条件，心机深沉的她反要借机对潘金莲下狠手，以除后患。",
                })
            except Exception as e:
                print(f"Error: {e}")


        fallback = None
        return fallback


async def main():
    scene_stream_by_chain_llm = SceneStreamByChainLLM(
        system_prompt=None
    )
    result = await scene_stream_by_chain_llm.arun(
        None, None, None, None, None
    )
    result = result.model_dump()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
