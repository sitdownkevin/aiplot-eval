.PHONY: run SceneInformation SceneChainAndNormEnding SceneStreamByChain SceneInteractionAndTrigger


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