from src.layers import build_default_pipeline


def test_layers_pipeline_returns_four_results():
    result = build_default_pipeline().run()
    assert len(result["results"]) == 4
    assert len(result["telemetry"]["traces"]) == 4
    assert result["final"]["output_tokens"] > 0
    assert result["final"]["token_reduction_ratio"] > 0
