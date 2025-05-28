import os
import asyncio
from langchain_core.runnables import Runnable
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = 0.8


class NextSceneInformationLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        
        self.llm = self.get_llm()
        self.output_parser = self.get_output_parser()
        self.prompt = self.get_prompt()
        self.chain = self.get_chain()

    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)

    def get_output_parser(self):
        response_schemas = [
            ResponseSchema(
                name="title", description="The title of the scene", type="string"),
            ResponseSchema(
                name="location", description="The location of the scene", type="string"),
            ResponseSchema(
                name="time", description="The time of the scene", type="string"),
            ResponseSchema(
                name="description", description="The description of the scene", type="string"),
        ]
        return StructuredOutputParser.from_response_schemas(response_schemas)

    def get_prompt(self):
        messages = []
        
        if self.system_prompt:
            system_template = SystemMessagePromptTemplate.from_template(self.system_prompt)
            messages.append(system_template)
            
        human_template = """
        <format_instructions>{format_instructions}</format_instructions>
    
        <task>
        生成一个场景的信息.
        </task>
    
        <example></example>

        <response_constraints>
        1. Use CHINESE to answer!
        2. Return the result in the format of `format_instructions`!
        </response_constraints>
        """
        
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        messages.append(human_message)
        
        chat_prompt = ChatPromptTemplate.from_messages(messages)
        
        return chat_prompt.partial(
            format_instructions=self.output_parser.get_format_instructions(),
        )

    def get_chain(self):
        return self.prompt | self.llm | self.output_parser

    def run(self):
        try:
            return self.chain.invoke({})
        except Exception as e:
            print(f"Error: {e}")
            return None

    async def arun(self):
        try:
            return await self.chain.ainvoke({})
        except Exception as e:
            print(f"Error: {e}")
            return None


async def main():
    next_scene_information_llm = NextSceneInformationLLM(
        system_prompt=None
    )
    result = await next_scene_information_llm.arun()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
