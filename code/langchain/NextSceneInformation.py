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
                name="scene_name", description="The name of the scene. Example: 老王烧饼铺.", type="string"),
            ResponseSchema(
                name="scene_location", description="The location of the scene. Example: 老王烧饼铺.", type="string"),
            ResponseSchema(
                name="scene_time", description="The time of the scene. Example: 上午十点.", type="string"),
            ResponseSchema(
                name="scene_description", description="The description of the scene. Example: 你来到隔壁老王的烧饼铺，蒸笼冒着热气却未见武大郎的摊位.", type="string"),
            ResponseSchema(
                name="character_name", description="The character of the scene. Example: 老王.", type="string"),
            ResponseSchema(
                name="character_description", description="The description of the character. Example: 隔壁老王四十余岁，满脸横肉，手臂有烫伤疤痕。因摊位纠纷与武大郎积怨已久，近日正在争夺早市黄金摊位.", type="string"),
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
        <goal>
        基于风格: "潘金莲{scene_style}", 生成一个场景的信息.
        </goal>
        
        <constraints>
        - 和潘金莲的剧情有关. 
        - 生成一个全新的角色，新的角色姓"{character_surname}"，人名的风格符合水浒的风格，并且要简单一些.
        - 生成的场景属于这位新角色，要有水浒风格.
        - 使用第二人称，对象是潘金莲.
        </constraints>
        </task>

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
            return await self.chain.ainvoke({
                "scene_style": random.choice([
                    "被质疑",
                    "被误解",
                    "被威胁",
                    "被欺骗",
                    "被利用",
                    "被背叛",
                    "被伤害",
                ]),
                "character_surname": random.choice([
                    "武",
                    "林",
                    "王",
                    "张",
                    "李",
                    "赵",
                    "孙",
                    "周",
                    "吴",
                    "郑",
                    "王",
                ]),
            })
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
