from src.algorithms.enhanced_hybrid import build_default_hybrid_registry
from src.tests.enhanced_hybrid import build_default_enhanced_hybrid_verifier


def test_enhanced_hybrid_registry_recommends_four_layers():
    registry = build_default_hybrid_registry()
    rec = registry.recommend(top_k=3)
    assert set(rec.keys()) == {'energy', 'compression', 'precision', 'compute'}
    assert any(item['name'] == 'platform_heterogeneous' for item in rec['energy'])
    assert any(item['name'] == 'cosmic_intelligence' for item in rec['compression'])


def test_enhanced_hybrid_verifier_passes():
    verifier = build_default_enhanced_hybrid_verifier()
    report = verifier.verify()
    assert report.passed is True
    assert report.failure_count == 0
    assert len(report.findings) == 4
