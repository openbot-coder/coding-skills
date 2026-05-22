# evolver — AHE 风格自我进化引擎
# 基于三大可观测性：组件可观测性、经验可观测性、决策可观测性
#
# 用法:
#   python -m evolver.cli analyze
#   python -m evolver.cli evolve
#   python -m evolver.cli report

from .collector import TraceCollector
from .evidence_distiller import EvidenceDistiller, Evidence
from .evolution_agent import EvolutionAgent
from .manifest import Manifest, load_manifests, evolution_stats, next_edit_id
from .verifier import Verifier
from .harness_map import HarnessMapper
from .evolver import EvolutionLoop

__all__ = [
    "TraceCollector",
    "EvidenceDistiller",
    "Evidence",
    "EvolutionAgent",
    "Manifest",
    "load_manifests",
    "evolution_stats",
    "next_edit_id",
    "Verifier",
    "HarnessMapper",
    "EvolutionLoop",
]
