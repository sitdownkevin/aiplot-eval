@echo off
rem 设置当前目录加入PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;.

rem 运行你的程序
@REM uv run streamlit test/test_offline.py
@REM uv run view.py
@REM uv run ./code/gai/SceneInformation.py
@REM uv run ./code/gai/SceneChainAndNormEnding.py
uv run ./code/gai/SceneStreamByChain.py
@REM uv run ./code/scriptwriter.py

rem 如果需要确保窗口不要自动关闭，可以加上一句
@REM pause