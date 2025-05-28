from code.scriptwriter import ScriptwriterAgent
import asyncio
import json


async def main():
    scriptwriter_agent = ScriptwriterAgent()
    result = await scriptwriter_agent.gen_new_scene_script()
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())