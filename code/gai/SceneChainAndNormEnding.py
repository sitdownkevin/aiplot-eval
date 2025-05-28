import os
import asyncio
import random
from langchain_core.runnables import Runnable
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from code.gai.schema import SceneInformationSchema, SceneChainAndNormEndingSchema, GamelogSchema, ScriptSchema


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = 0.8


class SceneChainAndNormEndingLLM:
    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt
        self.llm = self.get_llm()
        self.base_prompt = self.get_base_prompt()

    def get_llm(self):
        return ChatOpenAI(model=DEFAULT_OPENAI_MODEL_NAME, temperature=DEFAULT_OPENAI_TEMPERATURE)

    def get_output_parser(self):
        # 随机生成4-6之间的数字作为STREAM的数量
        stream_count = random.randint(4, 6)
        
        # 创建基本的response_schemas列表
        response_schemas = []
        
        # 动态添加STREAM
        for i in range(stream_count):
            stream_schema = ResponseSchema(
                name=f"CHAIN_{chr(65 + i)}", # 使用A, B, C, D, E, F作为后缀
                description="The chain of the scene.",
                type="string"
            )
            response_schemas.append(stream_schema)
        
        # 添加ENDING schema
        response_schemas.append(
            ResponseSchema(
                name="ENDING",
                description="The ending of the script",
                type="string"
            )
        )
        
        return StructuredOutputParser.from_response_schemas(response_schemas)

    def get_base_prompt(self):
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
        
        return ChatPromptTemplate.from_messages(messages)

    def get_prompt(self, output_parser):
        return self.base_prompt.partial(
            format_instructions=output_parser.get_format_instructions(),
        )

    def get_chain(self):
        output_parser = self.get_output_parser()
        prompt = self.get_prompt(output_parser)
        return prompt | self.llm | output_parser

    async def arun(self, 
                   gamelog: GamelogSchema,
                   script: ScriptSchema,
                   scene_information: SceneInformationSchema) -> SceneChainAndNormEndingSchema:
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

        return None


async def main():
    scene_chain_and_norm_ending_llm = SceneChainAndNormEndingLLM(
        system_prompt=None
    )
    result = await scene_chain_and_norm_ending_llm.arun(
        None, None, None
    )
    print(result)
    
    ending = result['ENDING']
    print(ending)


if __name__ == "__main__":
    asyncio.run(main())