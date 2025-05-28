.PHONY: SceneInformation SceneChainAndNormEnding run


SceneInformation:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneInformation.py

SceneChainAndNormEnding:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneChainAndNormEnding.py 

SceneStreamByChain:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/gai/SceneStreamByChain.py

run:
	PYTHONPATH=$PYTHONPATH:. uv run ./code/scriptwriter.py