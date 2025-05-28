import asyncio
from abc import ABC, abstractmethod
from code.config import Config
from code.llm import LLMProvider
from code.langchain.SceneInformation import SceneInformationLLM
from code.langchain.SceneChainAndNormEnding import SceneChainAndNormEndingLLM
from code.langchain.SceneStreamByChain import SceneStreamByChainLLM

class BaseScriptwriterAgent(ABC):
    def __init__(
        self,
        llm_model=Config.DRAMA_AGENT_MODEL_NAME,
        llm_provider=Config.DRAMA_AGENT_MODEL_PROVIDER,
    ):
        self._llm_model = llm_model
        self._llm_provider = LLMProvider(provider=llm_provider)

    async def gen_new_full_script(self) -> dict:
        """
        生成全部场景剧本（暂时待定）
        """
        pass

    @abstractmethod
    async def gen_new_scene_script(self, script: dict, gamelog: dict) -> dict:
        """
        生成一幕新场景剧本
        """
        pass


class ScriptwriterAgent(BaseScriptwriterAgent):
    def __init__(self,
        llm_model=Config.DRAMA_AGENT_MODEL_NAME,
        llm_provider=Config.DRAMA_AGENT_MODEL_PROVIDER,
    ):
        super().__init__(llm_model, llm_provider)
        
        self.scene_information_llm = SceneInformationLLM(system_prompt=None)
        self.scene_chain_and_norm_ending_llm = SceneChainAndNormEndingLLM(system_prompt=None)
        self.scene_stream_by_chain_llm = SceneStreamByChainLLM(system_prompt=None)

    async def gen_new_scene_script(self, script=None, gamelog=None):
        output_scene_name = None
        output_scene_description = None
        output_scene_character = None
        output_scene_plot_chain = []
        output_scene_stream = {}
        output_scene_interaction_conversation = []
        output_scene_interaction_action = []
        output_scene_trigger = {}
        output_scene_ending = None
        
        # 生成信息
        ## 生成场景信息
        scene_information = await self.scene_information_llm.arun(None, None)
        ## 生成情节链和结局
        scene_chain_and_norm_ending = await self.scene_chain_and_norm_ending_llm.arun(None, None, scene_information)
        ## 生成流
        chain_todo = [v for k, v in scene_chain_and_norm_ending.items()]
        tasks = []
        for i in range(len(chain_todo)-1):
            tasks.append(self.scene_stream_by_chain_llm.arun(None, 
                                                             None, 
                                                             scene_information, 
                                                             chain_todo[i],
                                                             chain_todo[i+1]))
        scene_stream_by_chain = await asyncio.gather(*tasks)
        print(scene_stream_by_chain)

        
        # 填充剧本
        output_scene_name = scene_information["scene_name"]
        output_scene_description = scene_information["scene_description"]
        output_scene_character = scene_information["character_name"]
        output_scene_plot_chain = [v for k, v in scene_chain_and_norm_ending.items() if "CHAIN_" in k]
        output_scene_ending = scene_chain_and_norm_ending["ENDING"]
        
        
        # DEBUG
        # route_evaluation = None
        # # TODO LLM 生成route_evaluation
        # print(route_evaluation)
        
        
        return {
            output_scene_name: {
                "场景": output_scene_description,
                "人物": output_scene_character,
                "情节链": output_scene_plot_chain,
                "流": output_scene_stream,
                "交互": {
                    "对话": output_scene_interaction_conversation,
                    "动作选择": output_scene_interaction_action,
                },
                "触发": output_scene_trigger,
                "结局18": {
                    "流": output_scene_ending,
                },
            }
        }