#!/usr/bin/env python3
"""Export lightweight Chart.js data for the Reveal presentation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler


CVSS_LABELS = ["0", "1", "2", "3", "4", "4.5", "5", "5.5", "6", "6.5", "7", "7.5", "8", "8.5", "9", "9.5", "10"]
CVSS_BINS = [-0.001, 1, 2, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10.001]
EPSS_LINEAR_LABELS = [
    "0-0.05", "0.05-0.1", "0.1-0.2", "0.2-0.3", "0.3-0.4", "0.4-0.5",
    "0.5-0.6", "0.6-0.7", "0.7-0.8", "0.8-0.9", "0.9-1.0",
]
EPSS_LINEAR_BINS = [0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.000001]
EPSS_LOG_LABELS = ["1e-5", "1e-4", "1e-3", "0.01", "0.1", "0.5", "1"]
EPSS_LOG_BINS = [0, 1e-5, 1e-4, 1e-3, 0.01, 0.1, 0.5, 1.000001]


def _histogram(series: pd.Series, bins: list[float]) -> list[int]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    counts, _ = np.histogram(values, bins=bins)
    return [int(value) for value in counts]


def _top_vendors(df: pd.DataFrame, limit: int = 10) -> dict[str, list]:
    counts = df["editeur"].fillna("Non disponible").value_counts().head(limit)
    return {"labels": counts.index.tolist(), "values": [int(value) for value in counts.values]}


def _severity_distribution(df: pd.DataFrame) -> dict[str, list]:
    filtered = df.dropna(subset=["cvss_score", "base_severity"]).copy()
    filtered = filtered[filtered["base_severity"] != "NONE"]
    counts = filtered["base_severity"].value_counts().sort_index()
    return {"labels": counts.index.tolist(), "values": [int(value) for value in counts.values]}


def _cwe_distribution(df: pd.DataFrame, limit: int = 8) -> dict[str, list]:
    filtered = df.dropna(subset=["cwe"]).copy()
    filtered = filtered[filtered["cwe"] != "Non disponible"]
    counts = filtered["cwe"].value_counts()
    top = counts.head(limit)
    return {"labels": top.index.tolist(), "values": [int(value) for value in top.values]}


def _ml_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    ml_df = df.dropna(subset=["cvss_score", "epss_score", "cwe"]).copy()
    ml_df = ml_df.drop_duplicates(subset=["cve"])
    ml_df["cvss_score"] = pd.to_numeric(ml_df["cvss_score"], errors="coerce")
    ml_df["epss_score"] = pd.to_numeric(ml_df["epss_score"], errors="coerce")
    ml_df = ml_df.dropna(subset=["cvss_score", "epss_score"])
    return ml_df


def _export_kmeans(ml_df: pd.DataFrame, random_state: int, max_points: int) -> dict:
    if len(ml_df) < 10:
        return {"silhouette": [], "elbow": [], "points": [], "clusterMeans": []}

    features = ml_df[["cvss_score", "epss_score"]].to_numpy()
    scaled = StandardScaler().fit_transform(features)

    silhouette_rows = []
    elbow_rows = []
    for k in range(2, 8):
        model = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = model.fit_predict(scaled)
        silhouette = silhouette_score(scaled, labels, sample_size=min(5000, len(scaled)), random_state=random_state)
        silhouette_rows.append({"k": k, "score": round(float(silhouette), 4)})
        elbow_rows.append({"k": k, "inertia": round(float(model.inertia_))})

    final_model = KMeans(n_clusters=3, random_state=random_state, n_init=10)
    ml_df = ml_df.copy()
    ml_df["cluster"] = final_model.fit_predict(scaled)

    samples = []
    per_cluster = max(1, max_points // 3)
    for cluster, group in ml_df.groupby("cluster"):
        sample = group.sample(n=min(per_cluster, len(group)), random_state=random_state)
        samples.append(sample)
    sampled = pd.concat(samples).sort_values(["cluster", "cve"])

    points = [
        {
            "x": round(float(row.cvss_score), 2),
            "y": round(float(np.log10(max(float(row.epss_score), 1e-5))), 4),
            "epss": round(float(row.epss_score), 6),
            "cluster": int(row.cluster),
        }
        for row in sampled.itertuples()
    ]

    means = (
        ml_df.groupby("cluster")[["cvss_score", "epss_score"]]
        .mean()
        .reset_index()
        .sort_values("cluster")
    )
    cluster_means = [
        {
            "cluster": int(row.cluster),
            "cvss": round(float(row.cvss_score), 2),
            "epss": round(float(row.epss_score), 4),
        }
        for row in means.itertuples()
    ]

    return {
        "silhouette": silhouette_rows,
        "elbow": elbow_rows,
        "points": points,
        "clusterMeans": cluster_means,
    }


def _export_knn(ml_df: pd.DataFrame, random_state: int) -> dict:
    ml_sup = ml_df.dropna(subset=["base_severity"]).copy()
    ml_sup = ml_sup[ml_sup["cwe"] != "Non disponible"].copy()
    ml_sup = ml_sup[ml_sup["base_severity"] != "NONE"].copy()

    class_counts = ml_sup["base_severity"].value_counts()
    if len(class_counts) < 2 or class_counts.min() < 5:
        return {"kValues": [], "means": [], "stds": [], "classResults": [], "accuracy": None, "bestK": None}

    cwe_encoder = LabelEncoder()
    ml_sup["cwe_encoded"] = cwe_encoder.fit_transform(ml_sup["cwe"].astype(str))
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(ml_sup["base_severity"])
    x = ml_sup[["epss_score", "cwe_encoded"]]

    k_values = [1, 3, 5, 7, 9, 11, 15]
    folds = min(5, int(class_counts.min()))
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=random_state)
    means = []
    stds = []
    for k in k_values:
        scores = cross_val_score(KNeighborsClassifier(n_neighbors=k), x, y, cv=cv)
        means.append(round(float(scores.mean()), 4))
        stds.append(round(float(scores.std()), 4))

    best_k = int(k_values[int(np.argmax(means))])
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=random_state, stratify=y
    )
    classifier = KNeighborsClassifier(n_neighbors=best_k)
    classifier.fit(x_train, y_train)
    y_pred = classifier.predict(x_test)

    labels = target_encoder.classes_
    class_results = []
    for label, encoded in zip(labels, range(len(labels))):
        true_positive = int(((y_test == encoded) & (y_pred == encoded)).sum())
        false_positive = int(((y_test != encoded) & (y_pred == encoded)).sum())
        false_negative = int(((y_test == encoded) & (y_pred != encoded)).sum())
        precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
        recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        class_results.append({"label": label, "f1": round(f1, 2)})

    accuracy = round(float((y_pred == y_test).mean()), 4)
    return {
        "kValues": k_values,
        "means": means,
        "stds": stds,
        "classResults": class_results,
        "accuracy": accuracy,
        "bestK": best_k,
    }


def build_presentation_data(df: pd.DataFrame, run_ml: bool = True, random_state: int = 42, max_kmeans_points: int = 1200) -> dict:
    df = df.copy()
    df["cvss_score"] = pd.to_numeric(df["cvss_score"], errors="coerce")
    df["epss_score"] = pd.to_numeric(df["epss_score"], errors="coerce")
    ml_df = _ml_dataframe(df)

    payload = {
        "meta": {
            "source_rows": int(len(df)),
            "unique_cves": int(df["cve"].nunique()),
            "unique_bulletins": int(df["id_anssi"].nunique()),
            "unique_vendors": int(df["editeur"].nunique()),
        },
        "cvssDistribution": {"labels": CVSS_LABELS, "values": _histogram(df["cvss_score"], CVSS_BINS)},
        "severityDistribution": _severity_distribution(df),
        "cweDistribution": _cwe_distribution(df),
        "epssLinear": {"labels": EPSS_LINEAR_LABELS, "values": _histogram(df["epss_score"], EPSS_LINEAR_BINS)},
        "epssLog": {"labels": EPSS_LOG_LABELS, "values": _histogram(df["epss_score"].clip(lower=1e-5), EPSS_LOG_BINS)},
        "topVendors": _top_vendors(df),
        "kmeans": {"silhouette": [], "elbow": [], "points": [], "clusterMeans": []},
        "knn": {"kValues": [], "means": [], "stds": [], "classResults": [], "accuracy": None, "bestK": None},
    }

    if run_ml:
        payload["kmeans"] = _export_kmeans(ml_df, random_state=random_state, max_points=max_kmeans_points)
        payload["knn"] = _export_knn(ml_df, random_state=random_state)

    return payload


def export_presentation_data(csv_path: Path | str, output_path: Path | str, run_ml: bool = True) -> dict:
    csv_path = Path(csv_path)
    output_path = Path(output_path)
    df = pd.read_csv(csv_path)
    payload = build_presentation_data(df, run_ml=run_ml)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Export presentation chart data from the consolidated ANSSI CSV.")
    parser.add_argument("--csv", type=Path, default=Path("data/vulnerabilites_anssi.csv"))
    parser.add_argument("--output", type=Path, default=Path("presentation/data/charts.json"))
    parser.add_argument("--skip-ml", action="store_true", help="Only export simple aggregates.")
    args = parser.parse_args()

    export_presentation_data(args.csv, args.output, run_ml=not args.skip_ml)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
