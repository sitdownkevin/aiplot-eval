from code.gai.schema import SceneStreamByChainSchema
import os
import asyncio
from langchain_core.runnables import Runnable
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
import random
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = 0.8


class SceneStreamByChainLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt

        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()

    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)

    def get_output_parser(self):
        scene_information_schemas = [
            ResponseSchema(
                name="TALK_A1",
                description="The talk of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="TALK_B1",
                description="The talk of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="TALK_A2",
                description="The talk of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="TALK_B2",
                description="The talk of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="TALK_A3",
                description="The talk of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="TALK_B3",
                description="The talk of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="KEY_TIP",
                description="The key tip of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="KEY_CLUE",
                description="The key clue of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
        ]

        return StructuredOutputParser.from_response_schemas(scene_information_schemas)


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
        基于情节链, 生成一个场景的信息.
        </goal>
        <constraints>
        - 和潘金莲的剧情有关. 
        - 生成的场景属于这位新角色，要有水浒风格.
        - 使用第二人称，对象是潘金莲.
        </constraints>
        <example>
        ```
        "潘金莲试探老王与武大郎的矛盾": [
            "老王（擦着擀面杖）：武大家的？稀客啊，你家那矮子今天怎舍得让娇妻抛头露面？",
            "潘金莲：王大哥说笑了，奴家来问问前日您说要买我家祖传和面方子的事...",
            "关键提示": "老王右手虎口有新鲜抓痕",
        ]
        ```
        </example>
        </task>

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
            format_instructions=self.output_parser.get_format_instructions(),
        )

    def get_chain(self):
        return self.prompt | self.llm | self.output_parser

    async def arun(self, 
                   gamelog,
                   script,
                   scene_information: str,
                   scene_chain: str,
                   next_scene_chain: str) -> SceneStreamByChainSchema:
        retries = 3
        
        for _ in range(retries):
            try:
                return await self.chain.ainvoke({
                    "gamelog": gamelog,
                    "script": script,
                    "scene_information": scene_information,
                    "scene_chain": scene_chain,
                    "next_scene_chain": next_scene_chain,
                })
            except Exception as e:
                print(f"Error: {e}")
        
        return None


async def main():
    scene_stream_by_chain_llm = SceneStreamByChainLLM(
        system_prompt=None
    )
    result = await scene_stream_by_chain_llm.arun(
        None, None, None, None, None
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
