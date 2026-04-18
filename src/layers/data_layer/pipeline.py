from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from .config import DataLayerConfig, DataSourceConfig
from .core import DataSource, DataSourceRegistry, DataCollectionResult


DEFAULT_SOURCE_CONFIGS = [
    DataSourceConfig(
        name='ccxt',
        source_type='exchange-aggregator',
        endpoint='ccxt://public',
        tags=['market', 'crypto', 'exchange'],
    ),
    DataSourceConfig(
        name='rss_news',
        source_type='news-feed',
        endpoint='rss://market-news',
        tags=['news', 'sentiment', 'macro'],
    ),
    DataSourceConfig(
        name='onchain',
        source_type='blockchain',
        endpoint='onchain://public',
        tags=['onchain', 'flows', 'wallet'],
    ),
    DataSourceConfig(
        name='filings',
        source_type='regulatory',
        endpoint='sec://filings',
        tags=['regulatory', 'fundamentals'],
    ),
]


class DataLayerPipeline:
    def __init__(self, config: DataLayerConfig | None = None, sources: List[DataSource] | None = None) -> None:
        self.config = config or DataLayerConfig()
        self.sources = sources or [DataSource(name=source.name, source_type=source.source_type, endpoint=source.endpoint, enabled=source.enabled, refresh_seconds=source.refresh_seconds, policy='compliant', tags=list(source.tags)) for source in DEFAULT_SOURCE_CONFIGS]

    def run(self) -> Dict[str, object]:
        selected = self.sources[: self.config.max_sources]
        collected: Dict[str, Dict[str, object]] = {}
        for source in selected:
            if source.name == 'ccxt':
                collected[source.name] = {
                    'status': 'available',
                    'markets': ['btc/usdt', 'eth/usdt'],
                    'adapter': 'ccxt',
                    'policy': source.policy,
                }
            elif source.name == 'rss_news':
                collected[source.name] = {
                    'status': 'available',
                    'items': 4,
                    'adapter': 'rss',
                    'policy': source.policy,
                }
            elif source.name == 'onchain':
                collected[source.name] = {
                    'status': 'available',
                    'flows': ['exchange_inflow', 'exchange_outflow'],
                    'adapter': 'onchain',
                    'policy': source.policy,
                }
            elif source.name == 'filings':
                collected[source.name] = {
                    'status': 'available',
                    'items': 2,
                    'adapter': 'regulatory',
                    'policy': source.policy,
                }
            else:
                collected[source.name] = {
                    'status': 'unavailable',
                    'adapter': source.source_type,
                    'policy': source.policy,
                }
        source_count = len(selected)
        compliant_sources = len([source for source in selected if source.policy == 'compliant'])
        return DataCollectionResult(
            collected=collected,
            summary={
                'source_count': source_count,
                'compliant_sources': compliant_sources,
                'dark_web_enabled': self.config.allow_dark_web,
                'budget': self.config.source_budget,
                'allow_third_party': self.config.allow_third_party,
                'allow_public_feeds': self.config.allow_public_feeds,
                'allow_onchain': self.config.allow_onchain,
                'allow_regulatory': self.config.allow_regulatory,
            },
        ).__dict__


def build_default_source_registry() -> DataSourceRegistry:
    sources = [DataSource(name=source.name, source_type=source.source_type, endpoint=source.endpoint, enabled=source.enabled, refresh_seconds=source.refresh_seconds, policy='compliant', tags=list(source.tags)) for source in DEFAULT_SOURCE_CONFIGS]
    return DataSourceRegistry(sources=sources, notes={'mode': 'compliant-public-data-only'})


def build_default_data_pipeline() -> DataLayerPipeline:
    return DataLayerPipeline()
