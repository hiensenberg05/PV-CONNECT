"""
Analytics Module for PV-CONNECT

Provides advanced signal detection and VigiGrade scoring for pharmacovigilance cases.
Includes BCPNN (Bayesian Confidence Propagation Neural Network) for WHO-standard signal detection.
"""

from .scoring import (
    VigiGradeScorer,
    calculate_score,
    update_case_score,
    batch_update_scores
)
from .vigigrade import router as vigigrade_router

# Import BCPNN components
try:
    from .bcpnn_engine import (
        BCPNNEngine,
        BCPNNResult,
        BCPNNIntegration,
        run_bcpnn_analysis,
        add_bcpnn_to_existing_signals
    )
    BCPNN_AVAILABLE = True
except ImportError:
    BCPNN_AVAILABLE = False
    BCPNNEngine = None
    BCPNNResult = None
    BCPNNIntegration = None
    run_bcpnn_analysis = None
    add_bcpnn_to_existing_signals = None

# Import enhanced analytics engine
try:
    from .analytics_engine_enhanced import (
        AnalyticsAggregator,
        EnhancedSignalDetector
    )
except ImportError:
    AnalyticsAggregator = None
    EnhancedSignalDetector = None

__all__ = [
    # VigiGrade scoring
    "VigiGradeScorer",
    "calculate_score", 
    "update_case_score",
    "batch_update_scores",
    "vigigrade_router",
    # BCPNN signal detection
    "BCPNNEngine",
    "BCPNNResult",
    "BCPNNIntegration",
    "run_bcpnn_analysis",
    "add_bcpnn_to_existing_signals",
    "BCPNN_AVAILABLE",
    # Enhanced analytics
    "AnalyticsAggregator",
    "EnhancedSignalDetector",
]
