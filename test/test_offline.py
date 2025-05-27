import sys

sys.path.insert(0, sys.path[0] + "/../")

import asyncio
import datetime
import json
import random

from lib.drama import DramaAgent


async def play(agent, inputs=None, action=None):
    if inputs is not None:
        inputs = (
            "To" + agent.script[agent.curr_scene]["人物"].split("。")[0] + "：" + inputs
        )
        api = await agent.update_by_user_input_1(inputs)
        api = await agent.update_by_user_input_2(inputs)
    elif action is not None:
        api = await agent.update_by_user_action(action)
    return api


async def run_once(retry=3):
    while retry > 0:
        try:
            agent = DramaAgent(
                script_path="./script/script_PanJinLian_v2.yml",
                open_dynamic_script=True,
            )
            await agent.init_scene(scene="序章")
            api = await play(agent, inputs="谁啊？", action=None)

            cnt = 0
            while not api["is_game_end"] and cnt <= 30:
                print("--------------------------------------")
                cnt += 1
                if (
                    len(api["default_user_input"]) == 0
                    and len(api["action_space"]) == 0
                ):
                    if api["is_game_end"]:
                        break

                    if api["scene_is_end"]:
                        print("跳转", api["next_scene"])
                        api = await agent.init_scene(scene=api["next_scene"])
                        continue
                    else:
                        break

                elif len(api["default_user_input"]) == 0:
                    interaction = "动作"
                elif len(api["action_space"]) == 0:
                    interaction = "对话"
                else:
                    if random.random() <= 0.6:
                        interaction = "对话"
                    else:
                        interaction = "动作"

                if interaction == "对话":
                    inputs = random.choice(api["default_user_input"])
                    print(interaction, inputs)
                    api = await play(agent, inputs=inputs, action=None)
                elif interaction == "动作":
                    if "离开$1" not in api["action_space"]:
                        action = random.choice(api["action_space"])
                    else:
                        if random.random() <= 0.2:
                            action = "离开$1"
                        else:
                            action_space = list(
                                set(api["action_space"]) - set(["离开$1"])
                            )
                            if len(action_space) == 0:
                                action = "离开$1"
                            else:
                                action = random.choice(action_space)

                    print(interaction, action)
                    api = await play(agent, inputs=None, action=action)
                    if api["is_game_end"]:
                        break
                    if api["scene_is_end"]:
                        print("跳转", api["next_scene"])
                        api = await agent.init_scene(scene=api["next_scene"])
            
            # Ending
            if agent.next_scene is not None and agent.next_scene.startswith("结局"):
                agent.log["结局"] = (
                    agent.next_scene + "：" + agent.ending[agent.next_scene]
                )
            else:
                agent.log["结局"] = "游戏超时，你被当做凶手逮捕！"
            print(agent.log)
            log = agent.log
            with open(
                "output/gamelog_{dt}.json".format(
                    dt=datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
                ),
                "w",
                encoding="utf-8",
            ) as wf:
                json.dump(log, wf, ensure_ascii=False)

            break
        except Exception as e:
            print(retry, e)
            retry -= 1


if __name__ == "__main__":
    asyncio.run(run_once(retry=1))
