from code.schema.SceneInformation import SceneInformation
import os
import asyncio
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
import random
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


# --- Configuration Constants ---
DEFAULT_OPENAI_MODEL_NAME = os.getenv(
    "OPENAI_MODEL_NAME", "gpt-4.1-mini")
DEFAULT_OPENAI_TEMPERATURE = 0.8

# --- Pydantic Output Parser ---
parser = PydanticOutputParser(pydantic_object=SceneInformation)


class SceneInformationLLM:
    def __init__(self, system_prompt: str = None, verbose: bool = False):
        self.system_prompt = system_prompt
        self.verbose = verbose

        self.llm = self.get_llm()
        self.prompt = self.get_prompt()
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
    
        <task>
        <goal>
        1. 生成一个新角色姓名，姓是: "{character_surname}"，起一个中国人名字，符合水浒风格.
        2. 新角色的身份基础是: {basic_charac_setting}，拥有几个符合{basic_charac_setting}特点的{basic_direction_setting}。基于上述内容，展开生成一个新角色的`character_description`.
        3. 基于上述内容，为新角色生成一个符合新角色的场景信息，提及"你 (即潘金莲)来到了这个场景".
        
        </goal>
        
        <constraints>
        1. 新角色{basic_socialnet_setting}.
        2. 生成角色的姓必须是: "{character_surname}".
        3. 生成的场景和这位新角色有关，要有水浒风格，绝对不可以是王婆家, 西门庆家和衙门.
        4. 场景的时间必须是上午十点.
        5. 场景的地点必须位于是县里，不可以出现现实地名，例如东京.
        6. `background_description`是从旁白视角向潘金莲进行讲述，直接用第二人称"你"来称呼潘金莲.
        7. `character_description`从第三人称视角描述.
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

    async def arun(self, gamelog, script) -> SceneInformation:
        retries = 3

        for _ in range(retries):
            try:
                # 创建配置字典（保持原始结构）
                config = {
                    "gamelog": gamelog,
                    "script": script,
                    # "basic_topic_setting": random.choice([
                    #     "复仇",
                    #     "替人办事",
                    #     "请人办事",
                    #     "陷害某人",
                    #     "帮助某人",
                    #     "做善事",
                    #     "泄愤",
                    #     "打劫",
                    #     "护送",
                    # ]),
                    "basic_charac_setting": random.choice([
                        "商贩",
                        "鬼魂",
                        "官差",
                        "地痞无赖",
                        "高官",
                        "道士",
                        "和尚",
                        "农夫渔夫",
                        "文人",
                        "武人",
                        "娼妓",
                        "大小姐",
                        "富人",
                    ]),
                    "basic_direction_setting": random.choice([
                        "邪恶的性格",
                        "正直的性格",
                    ]),
                    # "basic_act_setting": random.choice([
                    #     "妨碍潘金莲脱罪",
                    #     "帮助潘金莲脱罪",
                    #     "伤害潘金莲生命",
                    #     "帮潘金莲逃走",
                    # ]),
                    "basic_socialnet_setting": random.choice([
                        "认识潘金莲，知道她相貌美丽，性格贪婪，做事不择手段。发现潘金莲看起来很着急，像是做了坏事",
                        "不认识潘金莲，只看得出她相貌美丽，显得很着急",
                    ]),
                    "character_surname": random.choice([
                        "王", "李", "张", "刘", "陈", "杨", "黄", "吴", "赵", "周",
                        "徐", "孙", "马", "朱", "胡", "林", "郭", "何", "高", "罗",
                        "郑", "梁", "谢", "宋", "唐", "许", "邓", "冯", "韩", "曹",
                        "曾", "彭", "萧", "蔡", "潘", "田", "董", "袁", "于", "余",
                        "叶", "蒋", "杜", "苏", "魏", "程", "吕", "丁", "沈", "任",
                        "姚", "卢", "傅", "钟", "姜", "崔", "谭", "廖", "范", "汪",
                        "陆", "金", "石", "戴", "贾", "韦", "夏", "邱", "方", "侯",
                        "邹", "熊", "孟", "秦", "白", "江", "阎", "薛", "尹", "段",
                        "雷", "黎", "史", "龙", "陶", "贺", "顾", "毛", "郝", "龚",
                        "邵", "万", "钱", "严", "赖", "覃", "洪", "武", "莫", "孔"
                    ]),
                }
                
                if self.verbose:
                    print("随机生成配置:")
                    print(f"角色: {config['basic_charac_setting']}")
                    print(f"性格: {config['basic_direction_setting']}")
                    print(f"姓氏: {config['character_surname']}")
                    # print(f"基本目标: {config['basic_topic_setting']}")
                    # print(f"计划行动: {config['basic_act_setting']}")
                    print(f"社交情况: {config['basic_socialnet_setting']}")
                    

                # 保持原始调用方式不变
                return await self.chain.ainvoke(config)
            except Exception as e:
                print(f"Error: {e}")
                return None

        fallback = {
            "background": {
                "name": "孙二虎的草堂",
                "location": "清风寨山脚下的草堂",
                "time": "傍晚时分",
                "description": "你来到清风寨山脚下的草堂，夕阳的余晖洒在青瓦上，院内一片宁静，只有远处溪水潺潺。孙二虎正在院中整理草药，等待你的到来。"
            },
            "character": {
                "name": "孙二虎",
                "description": "孙二虎，身形魁梧，眉目刚毅，性格直爽豪爽，是清风寨的好汉之一。你曾在困境时得到他的帮助，他心怀正义，暗中关注着你的处境，愿为你出手相助。"
            }
        }
        return fallback


async def main():
    scene_information_llm = SceneInformationLLM(
        system_prompt=None, verbose=False
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

    import json
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
