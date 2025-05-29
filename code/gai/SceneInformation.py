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


class SceneInformationLLM:
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
                name="scene_name",
                description="The name of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="scene_location",
                description="The location of the scene. Example: 老王烧饼铺.",
                type="string"
            ),
            ResponseSchema(
                name="scene_time",
                description="The time of the scene. Example: 上午十点.",
                type="string"
            ),
            ResponseSchema(
                name="scene_description",
                description="The description of the scene. Example: 你来到隔壁老王的烧饼铺，蒸笼冒着热气却未见武大郎的摊位.",
                type="string"
            ),
            ResponseSchema(
                name="character_name",
                description="The character of the scene. Example: 老王.",
                type="string"
            ),
            ResponseSchema(
                name="character_description",
                description="The description of the character. Example: 隔壁老王四十余岁，满脸横肉，手臂有烫伤疤痕。因摊位纠纷与武大郎积怨已久，近日正在争夺早市黄金摊位.",
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
    
        <task>
        <goal>
        基于: "{basic_topic_setting}", 生成一个场景的信息.
        基于{basic_topic_setting}和{basic_charac_setting}, 生成新角色的`character_description`.
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

        human_message = HumanMessagePromptTemplate.from_template(
            human_template)
        messages.append(human_message)

        chat_prompt = ChatPromptTemplate.from_messages(messages)

        return chat_prompt.partial(
            format_instructions=self.output_parser.get_format_instructions(),
        )

    def get_chain(self):
        return self.prompt | self.llm | self.output_parser

    async def arun(self, gamelog, script) -> SceneInformationSchema:
        try:
            # 创建配置字典（保持原始结构）
            config = {
                "gamelog":gamelog,
                "script":script,
                "basic_topic_setting": random.choice([
                    "复仇",
                    "做买卖赚钱",
                    "替人办事",
                    "请人办事",
                    "陷害某人",
                    "帮助某人",
                    "做善事",
                    "泄愤",
                    "打劫",
                    "护送",
                    ""
                ]),
                "basic_charac_setting": random.choice([
                    "好汉",
                    "商贩",
                    "神鬼",
                    "官差",
                    "地痞无赖",
                    "高官",
                    "皇帝",
                    "道士",
                    "和尚",
                    "农夫渔夫",
                    "文人",
                    "武人",
                    "娼妓",
                    "大小姐",
                    "富人"
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
            }
            
            # 仅添加的打印语句（不改变任何原有逻辑）
            print("随机生成配置:")
            print(f"主题: {config['basic_topic_setting']}")
            print(f"角色: {config['basic_charac_setting']}")
            print(f"姓氏: {config['character_surname']}")
            
            # 保持原始调用方式不变
            return await self.chain.ainvoke(config)
        except Exception as e:
            print(f"Error: {e}")
            return None


async def main():
    scene_information_llm = SceneInformationLLM(
        system_prompt=None
    )

    # 读取YAML文件内容
    script_path = "script/script_PanJinLian_v2.yml"
    with open(script_path, 'r', encoding='utf-8') as file:
        script_content = file.read()

    
    # YAML文件内容传入script
    result = await scene_information_llm.arun(gamelog={
        "序章": {
        "潘金莲询问是谁": [
            "潘金莲：谁啊？",
            "郓哥（声音清晰，略带好奇）：我是郓哥，王婆家孩子，今天来看看大郎，怎么他没去摆摊呢？",
            "无匹配意图"
        ],
        "潘金莲询问郓哥来意": [
            "潘金莲：大郎在屋里，有些不舒服呢，你先别急着进来。",
            "郓哥（略显关切地说道）：嫂子，既然大郎不舒服，我明天再来看看。这几天他还好吗？",
            "潘金莲明确指出武大郎还在房间内$语义3",
            "潘金莲：你先别着急，等会儿我让你进来坐坐。",
            "郓哥（语气诚恳，目光中带着些许期待）：嫂子，那我进去坐坐也好，想亲自看看大郎是不是真的不舒服。",
            "潘金莲流露出让郓哥进来的意图$语义2",
            "潘金莲：你进来坐，等会儿我给你端热茶。",
            "郓哥（微笑着点头，语气诚恳）：谢谢嫂子，那我就进去坐坐，想看看大郎是不是真的不舒服。",
            "无匹配意图"
        ],
        "潘金莲决定如何回复郓哥": [
            "潘金莲：你放心，大郎很快就会好起来，别担心。",
            "郓哥（微笑着，目光诚恳）：谢谢嫂子，那我就进来坐坐，顺便亲自看看大郎的身体。",
            "无匹配意图"
        ],
        "郓哥透露武大郎和其他生意人隔壁老王的巨大矛盾": [
            "模仿武大说话$4",
            "你模仿武大的声音和郓哥说话，让郓哥离开了。"
        ]
    }
    }, script={script_content})
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
