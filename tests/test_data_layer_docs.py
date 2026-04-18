from pathlib import Path


def test_data_layer_docs_exist_and_describe_compliance():
    readme = Path('src/layers/data_layer/README.md').read_text(encoding='utf-8')
    doc = Path('docs/layers/data_layer.md').read_text(encoding='utf-8')
    assert 'ccxt' in readme.lower()
    assert 'dark web' not in readme.lower()
    assert 'compliant' in doc.lower()
    assert 'policy' in doc.lower()
