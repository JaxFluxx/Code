#!/usr/bin/env python3
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path("/Users/jia/Desktop/学习 /毕业设计")
EXPERIMENT_DIR = ROOT / "实验"
OUT_DIR = ROOT / "中期报告_20260402" / "outputs"

SAMPLE_SUMMARY = EXPERIMENT_DIR / "CODEX_clean_baseline" / "sample_summary.tsv"
PAIR_MANIFEST = EXPERIMENT_DIR / "CODEX_clean_baseline" / "pair_manifest.tsv"
STRATIFIED_STATS = (
    EXPERIMENT_DIR
    / "CODEX_pair_results_r20_r30_stratified"
    / "stratified_stats.tsv"
)
COHORT_ANALYSIS = (
    EXPERIMENT_DIR
    / "CODEX_pair_results_r20_r30_stratified"
    / "cohort_analysis.tsv"
)


def read_tsv(path):
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def write_tsv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def build_patient_sample_matrix(sample_rows):
    by_patient = defaultdict(dict)
    for row in sample_rows:
        by_patient[row["patient_id"]][row["sample_suffix"]] = row["sample_name"]

    matrix = []
    for patient_id in sorted(by_patient, key=lambda x: int(x)):
        row = {"patient_id": patient_id, "P": "", "L": "", "R": "", "QT": ""}
        row.update(by_patient[patient_id])
        matrix.append(row)
    return matrix


def build_analysis_scope(pair_rows):
    out = []
    for row in pair_rows:
        met_suffix = row["met_suffix"]
        analysis_scope = "主分析" if met_suffix in {"L", "R"} else "补充分析（不纳入卵巢转移主比较）"
        out.append(
            {
                "patient_id": row["patient_id"],
                "primary_sample": row["primary_sample"],
                "met_sample": row["met_sample"],
                "met_suffix": met_suffix,
                "analysis_scope": analysis_scope,
            }
        )
    return out


def build_key_result_table(stratified_rows):
    wanted = [
        ("R-only", "enrich_30_Tumor_M1"),
        ("R-only", "within_30_M2"),
        ("R-only", "m2_frac_of_mac"),
        ("L-only", "enrich_30_Tumor_M1"),
        ("L-only", "within_30_M2"),
        ("L-only", "m2_frac_of_mac"),
    ]
    keep = []
    for group, metric in wanted:
        for row in stratified_rows:
            if row["group"] == group and row["metric"] == metric:
                keep.append(
                    {
                        "group": row["group"],
                        "metric": row["metric"],
                        "n_pairs": row["n_pairs"],
                        "diff_mean": row["diff_mean"],
                        "diff_median": row["diff_median"],
                        "wilcoxon_p": row["wilcoxon_p"],
                    }
                )
                break
    return keep


def build_cohort_highlights(cohort_rows):
    wanted = [
        "m2_dist_median",
        "within_20_M2",
        "within_30_M2",
        "m2_frac_of_mac",
        "enrich_30_Tumor_M1",
    ]
    keep = []
    for row in cohort_rows:
        if row["section"] == "stats" and row["metric"] in wanted:
            keep.append(
                {
                    "metric": row["metric"],
                    "n_pairs": row["n_pairs"],
                    "diff_mean": row["diff_mean"],
                    "diff_median": row["diff_median"],
                    "wilcoxon_p": row["wilcoxon_p"],
                }
            )
    return keep


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sample_rows = read_tsv(SAMPLE_SUMMARY)
    pair_rows = read_tsv(PAIR_MANIFEST)
    stratified_rows = read_tsv(STRATIFIED_STATS)
    cohort_rows = read_tsv(COHORT_ANALYSIS)

    patient_matrix = build_patient_sample_matrix(sample_rows)
    analysis_scope = build_analysis_scope(pair_rows)
    key_results = build_key_result_table(stratified_rows)
    cohort_highlights = build_cohort_highlights(cohort_rows)

    write_tsv(
        OUT_DIR / "patient_sample_matrix.tsv",
        patient_matrix,
        ["patient_id", "P", "L", "R", "QT"],
    )
    write_tsv(
        OUT_DIR / "analysis_scope.tsv",
        analysis_scope,
        ["patient_id", "primary_sample", "met_sample", "met_suffix", "analysis_scope"],
    )
    write_tsv(
        OUT_DIR / "key_result_summary.tsv",
        key_results,
        ["group", "metric", "n_pairs", "diff_mean", "diff_median", "wilcoxon_p"],
    )
    write_tsv(
        OUT_DIR / "cohort_highlights.tsv",
        cohort_highlights,
        ["metric", "n_pairs", "diff_mean", "diff_median", "wilcoxon_p"],
    )


if __name__ == "__main__":
    main()
