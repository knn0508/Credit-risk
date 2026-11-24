from .aggregate_features import AggregateFeatures
from .application_features import ApplicationFeatures

__all__ = ["ApplicationFeatures", "AggregateFeatures"]

# decisions/0002 (təsdiqli): model feature-ı deyil, yalnız 05 fairness auditi üçün data-da qalır.
# 04 bunu bundle metadata.excluded_protected_features-ə yazır.
EXCLUDED_PROTECTED_FEATURES = ["code_gender"]
