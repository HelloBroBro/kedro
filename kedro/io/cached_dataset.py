"""
This module contains ``CachedDataset``, a dataset wrapper which caches in memory the data saved,
so that the user avoids io operations with slow storage media
"""

from __future__ import annotations

import logging
from typing import Any

from kedro.io.core import VERSIONED_FLAG_KEY, AbstractDataset, Version
from kedro.io.memory_dataset import MemoryDataset


class CachedDataset(AbstractDataset):
    """``CachedDataset`` is a dataset wrapper which caches in memory the data saved,
    so that the user avoids io operations with slow storage media.

    You can also specify a ``CachedDataset`` in catalog.yml:
    ::

        >>> test_ds:
        >>>    type: CachedDataset
        >>>    versioned: true
        >>>    dataset:
        >>>       type: pandas.CSVDataset
        >>>       filepath: example.csv

    Please note that if your dataset is versioned, this should be indicated in the wrapper
    class as shown above.
    """

    # this dataset cannot be used with ``ParallelRunner``,
    # therefore it has the attribute ``_SINGLE_PROCESS = True``
    # for parallelism please consider ``ThreadRunner`` instead
    _SINGLE_PROCESS = True

    def __init__(
        self,
        dataset: AbstractDataset | dict,
        version: Version | None = None,
        copy_mode: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Creates a new instance of ``CachedDataset`` pointing to the
        provided Python object.

        Args:
            dataset: A Kedro Dataset object or a dictionary to cache.
            version: If specified, should be an instance of
                ``kedro.io.core.Version``. If its ``load`` attribute is
                None, the latest version will be loaded. If its ``save``
                attribute is None, save version will be autogenerated.
            copy_mode: The copy mode used to copy the data. Possible
                values are: "deepcopy", "copy" and "assign". If not
                provided, it is inferred based on the data type.
            metadata: Any arbitrary metadata.
                This is ignored by Kedro, but may be consumed by users or external plugins.

        Raises:
            ValueError: If the provided dataset is not a valid dict/YAML
                representation of a dataset or an actual dataset.
        """
        self._EPHEMERAL = True

        if isinstance(dataset, dict):
            self._dataset = self._from_config(dataset, version)
        elif isinstance(dataset, AbstractDataset):
            self._dataset = dataset
        else:
            raise ValueError(
                "The argument type of 'dataset' should be either a dict/YAML "
                "representation of the dataset, or the actual dataset object."
            )
        self._cache = MemoryDataset(copy_mode=copy_mode)  # type: ignore[abstract]
        self.metadata = metadata

    def _release(self) -> None:
        self._cache.release()
        self._dataset.release()

    @staticmethod
    def _from_config(config: dict, version: Version | None) -> AbstractDataset:
        if VERSIONED_FLAG_KEY in config:
            raise ValueError(
                "Cached datasets should specify that they are versioned in the "
                "'CachedDataset', not in the wrapped dataset."
            )
        if version:
            config[VERSIONED_FLAG_KEY] = True
            return AbstractDataset.from_config(
                "_cached", config, version.load, version.save
            )
        return AbstractDataset.from_config("_cached", config)

    def _describe(self) -> dict[str, Any]:
        return {"dataset": self._dataset._describe(), "cache": self._cache._describe()}

    def __repr__(self) -> str:
        object_description = {
            "dataset": self._dataset._pretty_repr(self._dataset._describe()),
            "cache": self._dataset._pretty_repr(self._cache._describe()),
        }
        return self._pretty_repr(object_description)

    def _load(self) -> Any:
        data = self._cache.load() if self._cache.exists() else self._dataset.load()

        if not self._cache.exists():
            self._cache.save(data)

        return data

    def _save(self, data: Any) -> None:
        self._dataset.save(data)
        self._cache.save(data)

    def _exists(self) -> bool:
        return self._cache.exists() or self._dataset.exists()

    def __getstate__(self) -> dict[str, Any]:
        # clearing the cache can be prevented by modifying
        # how parallel runner handles datasets (not trivial!)
        logging.getLogger(__name__).warning("%s: clearing cache to pickle.", str(self))
        self._cache.release()
        return self.__dict__
