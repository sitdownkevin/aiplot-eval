.PHONY: SceneInformation SceneChainAndNormEnding


SceneInformation:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneInformation.py

SceneChainAndNormEnding:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneChainAndNormEnding.py 

SceneStreamByChain:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneStreamByChain.py

Scriptwriter:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/scriptwriter.py