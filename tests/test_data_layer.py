from src.layers.data_layer import build_default_data_pipeline, build_default_source_registry


def test_data_layer_registry_has_compliant_sources():
    registry = build_default_source_registry()
    names = [source.name for source in registry.sources]
    assert 'ccxt' in names
    assert 'rss_news' in names
    assert 'onchain' in names
    assert 'filings' in names
    assert 'dark_web' not in names


def test_data_layer_pipeline_produces_sources_and_summary():
    result = build_default_data_pipeline().run()
    assert result['summary']['source_count'] >= 4
    assert result['summary']['compliant_sources'] == result['summary']['source_count']
    assert result['summary']['dark_web_enabled'] is False
    assert 'ccxt' in result['collected']
    assert result['collected']['ccxt']['status'] in {'available', 'unavailable'}
