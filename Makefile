.PHONY: run SceneInformation SceneChainAndNormEnding SceneStreamByChain SceneInteractionAndTrigger

test:
	uv run ./test/test_offline.py

app:
	uv run streamlit run ./view.py

dev:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/scriptwriter.py

SceneInformation:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneInformation.py

SceneChainAndNormEnding:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneChainAndNormEnding.py 

SceneStreamByChain:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneStreamByChain.py

SceneInteractionAndTrigger:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneInteractionAndTrigger.py