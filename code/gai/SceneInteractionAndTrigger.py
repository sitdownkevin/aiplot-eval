from code.gai.schema import SceneInformationSchema
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


class SceneInteractionAndTriggerLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt

        self.base_prompt = self.get_base_prompt()
        self.llm = self.get_llm()

    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)

    def get_output_parser(self):
        conversation_number = random.randint(4, 6)
        action_number = random.randint(4, 6)
        
        scene_information_schemas = []
        for i in range(0, conversation_number):
            scene_information_schemas.extend([
                ResponseSchema(
                    name=f"CONVERSATION_NAME_{chr(65+i)}",
                    description="The name of the scene. Example: 老王烧饼铺.",
                    type="string"
                ),
                ResponseSchema(
                    name=f"CONVERSATION_CONDITION_{chr(65+i)}",
                    description="The name of the scene. Example: 老王烧饼铺.",
                    type="string"
                )
            ])
            
        for i in range(0, action_number):
            scene_information_schemas.extend([
                ResponseSchema(
                    name=f"ACTION_NAME_{chr(65+i)}",
                    description="The name of the scene. Example: 老王烧饼铺.",
                    type="string"
                ),
                ResponseSchema(
                    name=f"ACTION_CONDITION_{chr(65+i)}",
                    description="The name of the scene. Example: 老王烧饼铺.",
                    type="string"
                )
            ])

        return StructuredOutputParser.from_response_schemas(scene_information_schemas)


    def get_base_prompt(self):
        messages = []

        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(
                self.system_prompt)
            messages.append(system_template)

        human_template = """
        <format_instructions>{format_instructions}</format_instructions>
    
        <task>
        <goal>
        </goal>
        
        <constraints>
        - 和潘金莲的剧情有关. 
        - 生成的场景属于这位新角色，要有水浒风格.
        - 使用第二人称，对象是潘金莲.
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

        return ChatPromptTemplate.from_messages(messages)

    def get_prompt(self, output_parser):
        return self.base_prompt.partial(
            format_instructions=output_parser.get_format_instructions(),
        )

    def get_chain(self):
        output_parser = self.get_output_parser()
        prompt = self.get_prompt(output_parser)
        return prompt | self.llm | output_parser

    async def arun(self, gamelog, script) -> SceneInformationSchema:
        retries = 3

        for _ in range(retries):
            try:
                return await self.get_chain().ainvoke({
                    "gamelog": gamelog,
                    "script": script,
                })
            except Exception as e:
                print(f"Error: {e}")
                continue
            
        return None


async def main():
    scene_interaction_and_trigger_llm = SceneInteractionAndTriggerLLM(
        system_prompt=None
    )
    result = await scene_interaction_and_trigger_llm.arun(
        gamelog={}, 
        script={})
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
