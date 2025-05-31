@echo off
rem 设置当前目录加入PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;.

rem 运行你的程序
@REM uv run streamlit run view.py
@REM uv run ./code/gai/SceneInformation.py
@REM uv run ./code/gai/SceneChainAndNormEnding.py
@REM uv run ./code/gai/SceneStreamByChain.py
@REM uv run ./code/gai/SceneInteractionAndTrigger.py
@REM uv run ./code/scriptwriter.py
@REM uv run test/test_offline.py

rem 循环运行程序十次
for /l %%i in (1,1,3) do (
    echo running %%i ...
    uv run test/test_offline.py
    echo  %%i running end
    echo.
)

rem 如果需要确保窗口不要自动关闭，可以加上一句
@REM pause