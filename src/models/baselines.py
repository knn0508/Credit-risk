"""Baseline modellər. Preprocessing Pipeline daxilindədir → fit yalnız train fold-da."""
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def dummy(seed: int = 42):
    return DummyClassifier(strategy="prior", random_state=seed)


def logreg(seed: int = 42, class_weight=None):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, class_weight=class_weight, random_state=seed)),
    ])


FACTORIES = {"dummy": dummy, "logreg": logreg}
