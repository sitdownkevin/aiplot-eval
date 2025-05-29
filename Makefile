.PHONY: run SceneInformation SceneChainAndNormEnding SceneStreamByChain SceneInteractionAndTrigger

dev:
	uv run ./test/test_offline.py

app:
	uv run streamlit run ./view.py

run:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/scriptwriter.py

SceneInformation:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneInformation.py

SceneChainAndNormEnding:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneChainAndNormEnding.py 

SceneStreamByChain:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneStreamByChain.py

SceneInteractionAndTrigger:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneInteractionAndTrigger.py