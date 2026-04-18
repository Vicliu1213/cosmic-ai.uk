from src.algorithms.enhanced_classic import build_default_registry


def test_enhanced_classic_recommends_four_layers():
    registry = build_default_registry()
    rec = registry.recommend(top_k=3)
    assert set(rec.keys()) == {'energy', 'compression', 'precision', 'compute'}
    assert all(isinstance(v, list) for v in rec.values())
    assert any(item['name'] == 'platform_heterogeneous' for item in rec['energy'])
    assert any(item['name'] == 'cosmic_intelligence' for item in rec['compression'])


def test_enhanced_classic_to_index_contains_profiles():
    registry = build_default_registry()
    index = registry.to_index()
    assert 'profiles' in index
    assert len(index['profiles']) >= 10
    assert index['root']
