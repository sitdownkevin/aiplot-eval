from schema import NextSceneInformationSchema
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


class NextSceneInteractionByStreamLLM:
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
                name="action",
                description="The action of the scene. Example: 潘金莲发现武大郎的尸体后，惊慌失措，大声呼救。",
                type="string"
            ),
            ResponseSchema(
                name="conversation",
                description="The conversation of the action. Example: 潘金莲: 武大郎，你为什么死了？",
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
            <script>None</script>
            <gamelog>None</gamelog>
            <next_scene_information>王大姨的金店</next_scene_information>
            <next_scene_stream>王大姨发现了潘金莲杀害武大郎的事实</next_scene_stream>
        </game_information>
    
        <task>
        <goal>
        - 基于`game_information`, 生成一个潘金莲的动作
        - 基于`game_information`，生成可能的语义.
        </goal>
        
        <constraints>
        - 和潘金莲的剧情有关. 
        - 生成的场景属于这位新角色，要有水浒风格.
        - 使用第三人称，对象是潘金莲.
        </constraints>
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

    async def arun(self):
        retries = 3

        for _ in range(retries):
            try:
                return await self.chain.ainvoke({})
            except Exception as e:
                print(f"Error: {e}")

        return None


async def main():
    next_scene_interaction_by_stream_llm = NextSceneInteractionByStreamLLM(
        system_prompt=None
    )
    result = await next_scene_interaction_by_stream_llm.arun()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
