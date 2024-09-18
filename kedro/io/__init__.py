"""``kedro.io`` provides functionality to read and write to a
number of data sets. At the core of the library is the ``AbstractDataset`` class.
"""

from __future__ import annotations

from .cached_dataset import CachedDataset
from .catalog_config_resolver import CatalogConfigResolver
from .core import (
    AbstractDataset,
    AbstractVersionedDataset,
    CatalogProtocol,
    DatasetAlreadyExistsError,
    DatasetError,
    DatasetNotFoundError,
    Version,
)
from .data_catalog import DataCatalog
from .lambda_dataset import LambdaDataset
from .memory_dataset import MemoryDataset
from .shared_memory_dataset import SharedMemoryDataset

__all__ = [
    "AbstractDataset",
    "AbstractVersionedDataset",
    "CachedDataset",
    "CatalogProtocol",
    "DataCatalog",
    "CatalogConfigResolver",
    "DatasetAlreadyExistsError",
    "DatasetError",
    "DatasetNotFoundError",
    "LambdaDataset",
    "MemoryDataset",
    "SharedMemoryDataset",
    "Version",
]
