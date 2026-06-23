"""Reference-based (offline) metrics: the ``score()`` side of ``ke``.

A :class:`~ke.base.Metric` compares one prediction to one gold reference and
returns a :class:`~ke.base.Score`. The *right* metric is a function of the output
**object type** -- a string wants CER/WER, a record wants field-level F1, a table
wants TEDS/GriTS, a typed graph wants a cost-weighted edit distance. This package
holds the concrete metrics and registers each under the ``"metrics"`` namespace so
the :func:`~ke.facade.score` facade can dispatch by type or by name.

Shipping now (zero/low-dependency, in core): :class:`StringMetric` (CER/WER, via
``jiwer`` when present) and :class:`FieldMetric` (record/dict field F1). The richer
metrics (ANLS*, span-F1 via ``seqeval``/``nervaluate``, TEDS/GriTS, and the
flagship cost-weighted typed-graph distance) arrive behind the ``[metrics]`` extra
-- see the project roadmap and ``misc/docs/ke_02``.
"""

from __future__ import annotations

from ..registry import register
from .fields import FieldMetric
from .strings import StringMetric

# Register the built-in metrics (idempotent; import side effect).
register("metrics", "cer", StringMetric(mode="cer"))
register("metrics", "wer", StringMetric(mode="wer"))
register("metrics", "fields", FieldMetric())

__all__ = ["StringMetric", "FieldMetric"]
