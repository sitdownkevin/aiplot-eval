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
        <script>{script}</script>
        <gamelog>{gamelog}</gamelog>
        <current_scene_information>{scene_information}</current_scene_information>
        </game_information>
    
        <task>
        生成一个流和正常的结局的剧本.
        </task>
    
        <example>
        1. 潘金莲试探老王与武大郎的矛盾
        2. 老王察觉潘金莲异常神色
        3. 潘金莲试图用砒霜栽赃老王
        4. 老王反咬潘金莲通奸之事
        5. 烧饼铺伙计目击争执
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
                return await chain.ainvoke({
                    'scene_information': scene_information,
                    'gamelog': gamelog,
                    'script': script,
                })
            except Exception as e:
                print(f"Error: {e}")
                continue

        fallback = None
        return fallback


async def main():
    scene_chain_and_norm_ending_llm = SceneChainAndNormEndingLLM(
        system_prompt=None,
        verbose=True
    )
    
    result = await scene_chain_and_norm_ending_llm.arun(
        None, None, None
    )
    result = result.model_dump()
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())