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

from code.schema.SceneInteractionAndTrigger import SceneInteractionAndTrigger
from langchain_core.output_parsers import PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=SceneInteractionAndTrigger)


class SceneInteractionAndTriggerLLM:
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
        <history_rounds>{history_rounds}</history_rounds>
        <current_round>{current_round}</current_round>
        </game_information>
    
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

        chat_prompt = ChatPromptTemplate.from_messages(messages)

        return chat_prompt.partial(
            format_instructions=parser.get_format_instructions(),
        )

    def get_chain(self):
        return self.prompt | self.llm | parser

    async def arun(self,
                   gamelog,
                   script,
                   history_rounds,
                   current_round) -> SceneInteractionAndTrigger:
        retries = 3

        for _ in range(retries):
            try:
                return await self.get_chain().ainvoke({
                    "gamelog": gamelog,
                    "script": script,
                    "history_rounds": history_rounds,
                    "current_round": current_round,
                })
            except Exception as e:
                print(f"Error: {e}")
                continue

        fallback = None

        return fallback


async def main():
    scene_interaction_and_trigger_llm = SceneInteractionAndTriggerLLM(
        system_prompt=None
    )
    result = await scene_interaction_and_trigger_llm.arun(
        gamelog={},
        script={},
        history_rounds=[],
        current_round={}
    )

    result = result.model_dump()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
