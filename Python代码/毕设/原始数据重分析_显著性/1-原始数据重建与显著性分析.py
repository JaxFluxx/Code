from pathlib import Path
import re
import shutil

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree
from scipy.stats import wilcoxon


RAW_ROOT = Path("/Users/jia/Desktop/学习 /毕业设计/实验/CODEX全部分析数据-20260116")
OUT_DIR = Path("/Users/jia/Desktop/学习 /毕业设计/实验/CODEX_raw_reanalysis_significance")
SAMPLES_OUT_DIR = OUT_DIR / "samples"

SAMPLE_SUMMARY_PATH = OUT_DIR / "sample_summary.tsv"
PAIR_MANIFEST_PATH = OUT_DIR / "pair_manifest.tsv"
PAIR_METRICS_PATH = OUT_DIR / "pair_metrics.tsv"
SIGNIFICANCE_PATH = OUT_DIR / "paired_significance.tsv"

MIN_M1_THRESHOLD = 50

plt.rcParams["axes.unicode_minus"] = False

PRIMARY_COLOR = "#2B6CB0"
MET_COLOR = "#C53030"
ACCENT_COLOR = "#2F855A"
GRID_COLOR = "#D9D9D9"

METRIC_LABELS = {
    "m1_to_tumor": "M1 / Tumor",
    "enrich_20_Tumor_M1": "Tumor-M1互作(20)",
    "enrich_30_Tumor_M1": "Tumor-M1互作(30)",
    "m2_dist_median": "M2到最近Tumor中位距离",
    "within_20_M2": "20内贴Tumor的M2比例",
    "within_30_M2": "30内贴Tumor的M2比例",
    "m2_frac_of_mac": "M2 / (M1 + M2)",
    "m1_frac_of_mac": "M1 / (M1 + M2)",
    "m2_to_tumor": "M2 / Tumor",
    "mac_to_tumor": "Mac / Tumor",
}

SIGNIFICANCE_METRICS = [
    "diff_m1_to_tumor",
    "diff_enrich_20_Tumor_M1",
    "diff_enrich_30_Tumor_M1",
    "diff_m2_dist_median",
    "diff_within_20_M2",
    "diff_within_30_M2",
    "diff_m2_frac_of_mac",
    "diff_m2_to_tumor",
]


def norm_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


def format_value(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def round_numeric(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]):
            out[col] = out[col].round(2)
    return out


def parse_sample_name(sample_name: str) -> tuple[int | None, str | None]:
    match = re.match(r"^(\d+)(P|L|R|QT)$", str(sample_name).strip(), flags=re.IGNORECASE)
    if not match:
        return None, None
    return int(match.group(1)), match.group(2).upper()


def find_largest_objects_file(sample_dir: Path) -> Path | None:
    candidates = [path for path in sample_dir.iterdir() if path.is_file() and "objects" in path.name.lower()]
    return max(candidates, key=lambda path: path.stat().st_size) if candidates else None


def pick_col(columns: list[str], aliases: list[str], prefer_contains: list[str] | None = None) -> str | None:
    norm_map = {col: norm_text(col) for col in columns}
    candidates = [col for col in columns if any(alias in norm_map[col] for alias in aliases)]
    if not candidates:
        return None
    if prefer_contains:
        preferred = [col for col in candidates if all(key in norm_map[col] for key in prefer_contains)]
        if preferred:
            candidates = preferred
    candidates = sorted(candidates, key=lambda col: (len(norm_map[col]), len(str(col))))
    return candidates[0]


def detect_required_columns(df: pd.DataFrame) -> dict[str, str | None]:
    cols = list(df.columns)
    col_map = {
        "cell_id": pick_col(cols, aliases=["objectid", "cellid", "id", "objectnumber"]),
        "x": pick_col(cols, aliases=["centerx", "centroidx", "xcenter", "positionx", "locationx", "xcoord", "coordx"]),
        "y": pick_col(cols, aliases=["centery", "centroidy", "ycenter", "positiony", "locationy", "ycoord", "coordy"]),
        "panck": pick_col(cols, aliases=["pancytokeratin", "panck"], prefer_contains=["positivity"]) or pick_col(cols, aliases=["pancytokeratin", "panck"]),
        "cd68": pick_col(cols, aliases=["cd68"], prefer_contains=["positivity"]) or pick_col(cols, aliases=["cd68"]),
        "cd86": pick_col(cols, aliases=["cd86"], prefer_contains=["positivity"]) or pick_col(cols, aliases=["cd86"]),
        "cd163": pick_col(cols, aliases=["cd163"], prefer_contains=["positivity"]) or pick_col(cols, aliases=["cd163"]),
    }
    missing = [key for key, value in col_map.items() if key != "cell_id" and value is None]
    if missing:
        raise ValueError(f"缺少关键列：{missing}")
    return col_map


def to_numeric_binary(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    return (values > 0.5).astype(np.int8)


def cell_type_from_flags(row: pd.Series) -> str:
    if row["is_tumor"] == 1:
        return "Tumor"
    if row["is_m1"] == 1:
        return "M1"
    if row["is_m2"] == 1:
        return "M2"
    if row["is_ambiguous_mac"] == 1:
        return "Ambiguous_Mac"
    if row["is_mac"] == 1:
        return "Mac_other"
    return "Other"


def safe_div(a: float, b: float) -> float:
    if b == 0 or pd.isna(b):
        return np.nan
    return float(a) / float(b)


def get_coords(df: pd.DataFrame, cell_type: str) -> np.ndarray:
    sub = df[df["cell_type"] == cell_type]
    if sub.empty:
        return np.empty((0, 2), dtype=float)
    return sub[["Center X", "Center Y"]].to_numpy(dtype=float)


def within_r_ratio(src_coords: np.ndarray, tgt_coords: np.ndarray, radius: float) -> float:
    if len(src_coords) == 0 or len(tgt_coords) == 0:
        return np.nan
    distances, _ = cKDTree(tgt_coords).query(src_coords, k=1)
    distances = np.asarray(distances, dtype=float)
    return float(np.mean(distances <= radius))


def avg_count_within_radius(center_coords: np.ndarray, target_coords: np.ndarray, radius: float) -> float:
    if len(center_coords) == 0 or len(target_coords) == 0:
        return np.nan
    counts = cKDTree(target_coords).query_ball_point(center_coords, r=radius, return_length=True)
    return float(np.mean(np.asarray(counts, dtype=float)))


def median_nearest_distance(src_coords: np.ndarray, tgt_coords: np.ndarray) -> float:
    if len(src_coords) == 0 or len(tgt_coords) == 0:
        return np.nan
    distances, _ = cKDTree(tgt_coords).query(src_coords, k=1)
    distances = np.asarray(distances, dtype=float)
    distances = distances[np.isfinite(distances)]
    return float(np.median(distances)) if len(distances) else np.nan


def preprocess_raw_samples() -> tuple[pd.DataFrame, pd.DataFrame]:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    SAMPLES_OUT_DIR.mkdir(parents=True, exist_ok=True)

    sample_summary_rows = []
    pair_index: dict[int, dict[str, dict]] = {}

    sample_dirs = sorted([path for path in RAW_ROOT.iterdir() if path.is_dir()], key=lambda path: path.name)
    print(f"共发现原始样本文件夹：{len(sample_dirs)}")

    for sample_dir in sample_dirs:
        sample_name = sample_dir.name.strip()
        patient_id, suffix = parse_sample_name(sample_name)
        if patient_id is None:
            continue

        objects_file = find_largest_objects_file(sample_dir)
        if objects_file is None:
            continue

        header_df = pd.read_csv(objects_file, sep="\t", nrows=0)
        col_map = detect_required_columns(header_df)
        usecols = [col_map[key] for key in ["x", "y", "panck", "cd68", "cd86", "cd163"]]
        if col_map["cell_id"] is not None:
            usecols.append(col_map["cell_id"])
        usecols = list(dict.fromkeys(usecols))
        df = pd.read_csv(objects_file, sep="\t", usecols=usecols, low_memory=False)

        cell_id = df[col_map["cell_id"]] if col_map["cell_id"] is not None else pd.Series(np.arange(len(df)), index=df.index)
        clean = pd.DataFrame(
            {
                "cell_id": cell_id,
                "Center X": pd.to_numeric(df[col_map["x"]], errors="coerce"),
                "Center Y": pd.to_numeric(df[col_map["y"]], errors="coerce"),
                "PanCK": to_numeric_binary(df[col_map["panck"]]),
                "CD68": to_numeric_binary(df[col_map["cd68"]]),
                "CD86": to_numeric_binary(df[col_map["cd86"]]),
                "CD163": to_numeric_binary(df[col_map["cd163"]]),
            }
        )
        clean["sample_name"] = sample_name
        clean["patient_id"] = patient_id
        clean["sample_suffix"] = suffix
        clean["source_file"] = str(objects_file)
        clean = clean.dropna(subset=["Center X", "Center Y"]).copy()

        clean["is_tumor"] = ((clean["PanCK"] == 1) & (clean["CD68"] == 0)).astype(np.int8)
        clean["is_mac"] = ((clean["CD68"] == 1) & (clean["PanCK"] == 0)).astype(np.int8)
        clean["is_m1"] = ((clean["CD68"] == 1) & (clean["CD86"] == 1) & (clean["CD163"] == 0) & (clean["PanCK"] == 0)).astype(np.int8)
        clean["is_m2"] = ((clean["CD68"] == 1) & (clean["CD163"] == 1) & (clean["CD86"] == 0) & (clean["PanCK"] == 0)).astype(np.int8)
        clean["is_ambiguous_mac"] = ((clean["CD68"] == 1) & (clean["CD86"] == 1) & (clean["CD163"] == 1) & (clean["PanCK"] == 0)).astype(np.int8)
        clean["cell_type"] = clean.apply(cell_type_from_flags, axis=1)

        analysis_cells = clean[clean["cell_type"].isin(["Tumor", "M1", "M2"])].copy()

        sample_out_dir = SAMPLES_OUT_DIR / sample_name
        sample_out_dir.mkdir(parents=True, exist_ok=True)
        clean_all_path = sample_out_dir / f"{sample_name}_clean_all.tsv"
        analysis_path = sample_out_dir / f"{sample_name}_analysis_cells.tsv"
        clean.to_csv(clean_all_path, sep="\t", index=False)
        analysis_cells.to_csv(analysis_path, sep="\t", index=False)

        tumor_n = int((analysis_cells["cell_type"] == "Tumor").sum())
        m1_n = int((analysis_cells["cell_type"] == "M1").sum())
        m2_n = int((analysis_cells["cell_type"] == "M2").sum())
        mac_n = m1_n + m2_n

        sample_summary_rows.append(
            {
                "patient_id": patient_id,
                "sample_name": sample_name,
                "sample_suffix": suffix,
                "source_file": str(objects_file),
                "n_total_clean_rows": int(len(clean)),
                "tumor_n": tumor_n,
                "m1_n": m1_n,
                "m2_n": m2_n,
                "m2_frac_of_mac": safe_div(m2_n, mac_n),
                "clean_all_path": str(clean_all_path),
                "analysis_cells_path": str(analysis_path),
            }
        )

        pair_index.setdefault(patient_id, {})[suffix] = {
            "sample_name": sample_name,
            "clean_all_path": str(clean_all_path),
            "analysis_cells_path": str(analysis_path),
        }

    sample_summary_df = pd.DataFrame(sample_summary_rows).sort_values(["patient_id", "sample_name"]).reset_index(drop=True)
    pair_rows = []
    for patient_id, sample_map in sorted(pair_index.items()):
        if "P" not in sample_map:
            continue
        for met_suffix in ["L", "R", "QT"]:
            if met_suffix not in sample_map:
                continue
            primary = sample_map["P"]
            met = sample_map[met_suffix]
            pair_rows.append(
                {
                    "patient_id": patient_id,
                    "primary_sample": primary["sample_name"],
                    "met_sample": met["sample_name"],
                    "met_suffix": met_suffix,
                    "primary_clean_all_path": primary["clean_all_path"],
                    "primary_analysis_path": primary["analysis_cells_path"],
                    "met_clean_all_path": met["clean_all_path"],
                    "met_analysis_path": met["analysis_cells_path"],
                }
            )
    pair_manifest_df = pd.DataFrame(pair_rows).sort_values(["met_suffix", "patient_id", "met_sample"]).reset_index(drop=True)

    round_numeric(sample_summary_df).to_csv(SAMPLE_SUMMARY_PATH, sep="\t", index=False)
    pair_manifest_df.to_csv(PAIR_MANIFEST_PATH, sep="\t", index=False)
    return sample_summary_df, pair_manifest_df


def load_sample_metrics(sample_path: Path) -> dict[str, float]:
    df = pd.read_csv(sample_path, sep="\t")
    tumor_coords = get_coords(df, "Tumor")
    m1_coords = get_coords(df, "M1")
    m2_coords = get_coords(df, "M2")

    tumor_n = len(tumor_coords)
    m1_n = len(m1_coords)
    m2_n = len(m2_coords)
    mac_n = m1_n + m2_n

    metrics = {
        "tumor_n": tumor_n,
        "m1_n": m1_n,
        "m2_n": m2_n,
        "mac_n": mac_n,
        "m1_to_tumor": safe_div(m1_n, tumor_n),
        "m2_to_tumor": safe_div(m2_n, tumor_n),
        "mac_to_tumor": safe_div(mac_n, tumor_n),
        "m1_frac_of_mac": safe_div(m1_n, mac_n),
        "m2_frac_of_mac": safe_div(m2_n, mac_n),
        "within_20_M1": within_r_ratio(m1_coords, tumor_coords, 20),
        "within_20_M2": within_r_ratio(m2_coords, tumor_coords, 20),
        "within_30_M1": within_r_ratio(m1_coords, tumor_coords, 30),
        "within_30_M2": within_r_ratio(m2_coords, tumor_coords, 30),
        "enrich_20_Tumor_M1": avg_count_within_radius(tumor_coords, m1_coords, 20),
        "enrich_20_Tumor_M2": avg_count_within_radius(tumor_coords, m2_coords, 20),
        "enrich_30_Tumor_M1": avg_count_within_radius(tumor_coords, m1_coords, 30),
        "enrich_30_Tumor_M2": avg_count_within_radius(tumor_coords, m2_coords, 30),
        "m1_dist_median": median_nearest_distance(m1_coords, tumor_coords),
        "m2_dist_median": median_nearest_distance(m2_coords, tumor_coords),
    }
    metrics["dist_gap_m2_minus_m1"] = (
        metrics["m2_dist_median"] - metrics["m1_dist_median"]
        if pd.notna(metrics["m1_dist_median"]) and pd.notna(metrics["m2_dist_median"])
        else np.nan
    )
    return metrics


def build_pair_metrics(pair_manifest_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in pair_manifest_df.iterrows():
        primary_metrics = load_sample_metrics(Path(row["primary_analysis_path"]))
        met_metrics = load_sample_metrics(Path(row["met_analysis_path"]))
        out = {
            "group": row["met_suffix"],
            "patient_id": int(row["patient_id"]),
            "pair_label": f'{row["primary_sample"]} vs {row["met_sample"]}',
            "primary_sample": row["primary_sample"],
            "met_sample": row["met_sample"],
        }
        out.update({f"primary_{key}": value for key, value in primary_metrics.items()})
        out.update({f"met_{key}": value for key, value in met_metrics.items()})
        for key in primary_metrics:
            p_value = primary_metrics[key]
            m_value = met_metrics[key]
            out[f"diff_{key}"] = m_value - p_value if pd.notna(p_value) and pd.notna(m_value) else np.nan
        rows.append(out)
    pair_metrics_df = pd.DataFrame(rows).sort_values(["group", "patient_id"]).reset_index(drop=True)
    round_numeric(pair_metrics_df).to_csv(PAIR_METRICS_PATH, sep="\t", index=False)
    return pair_metrics_df


def paired_wilcoxon(values: pd.Series) -> tuple[float, int]:
    x = values.dropna().to_numpy(dtype=float)
    if len(x) < 2:
        return np.nan, len(x)
    try:
        return float(wilcoxon(x, zero_method="pratt").pvalue), len(x)
    except Exception:
        return np.nan, len(x)


def build_significance_table(pair_metrics_df: pd.DataFrame) -> pd.DataFrame:
    subsets = [
        ("ALL", "all_pairs", pair_metrics_df),
        ("R", "all_pairs", pair_metrics_df[pair_metrics_df["group"] == "R"]),
        ("L", "all_pairs", pair_metrics_df[pair_metrics_df["group"] == "L"]),
        ("QT", "all_pairs", pair_metrics_df[pair_metrics_df["group"] == "QT"]),
        (
            "R",
            f"min_m1_both_{MIN_M1_THRESHOLD}",
            pair_metrics_df[
                (pair_metrics_df["group"] == "R")
                & (pair_metrics_df["primary_m1_n"] >= MIN_M1_THRESHOLD)
                & (pair_metrics_df["met_m1_n"] >= MIN_M1_THRESHOLD)
            ],
        ),
    ]

    rows = []
    for group, filter_name, sub_df in subsets:
        for metric in SIGNIFICANCE_METRICS:
            p_value, n_pairs = paired_wilcoxon(sub_df[metric]) if metric in sub_df.columns else (np.nan, 0)
            vals = sub_df[metric].dropna() if metric in sub_df.columns else pd.Series(dtype=float)
            rows.append(
                {
                    "group": group,
                    "filter_name": filter_name,
                    "metric": metric,
                    "n_pairs": n_pairs,
                    "mean_diff": float(vals.mean()) if len(vals) else np.nan,
                    "median_diff": float(vals.median()) if len(vals) else np.nan,
                    "wilcoxon_p": p_value,
                }
            )
    significance_df = round_numeric(pd.DataFrame(rows))
    significance_df.to_csv(SIGNIFICANCE_PATH, sep="\t", index=False)
    return significance_df


def annotate_pair_stats(ax, sub_df: pd.DataFrame, diff_col: str, p_value: float) -> None:
    vals = sub_df[diff_col].dropna().to_numpy(dtype=float)
    if len(vals) == 0:
        text = "无有效配对"
    else:
        text = (
            f"n={len(vals)}\n"
            f"平均差={format_value(np.mean(vals))}\n"
            f"中位差={format_value(np.median(vals))}\n"
            f"p={format_value(p_value, 4) if pd.notna(p_value) else 'NA'}"
        )
    ax.text(
        0.03,
        0.97,
        text,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.5,
        color=ACCENT_COLOR,
        bbox={"facecolor": "white", "edgecolor": "#DDDDDD", "alpha": 0.9},
    )


def draw_paired_lines(ax, sub_df: pd.DataFrame, metric: str, title: str) -> None:
    p_col = f"primary_{metric}"
    m_col = f"met_{metric}"
    d_col = f"diff_{metric}"
    plot_df = sub_df[["pair_label", p_col, m_col, d_col]].dropna().reset_index(drop=True)
    if plot_df.empty:
        ax.axis("off")
        ax.set_title(title)
        return

    for _, row in plot_df.iterrows():
        pv = float(row[p_col])
        mv = float(row[m_col])
        ax.plot([0, 1], [pv, mv], color="#8A8A8A", linewidth=1.3, alpha=0.75, zorder=1)
        ax.scatter([0], [pv], color=PRIMARY_COLOR, s=34, zorder=2)
        ax.scatter([1], [mv], color=MET_COLOR, s=34, zorder=2)

    mean_p = float(plot_df[p_col].mean())
    mean_m = float(plot_df[m_col].mean())
    ax.plot([0, 1], [mean_p, mean_m], color="#111111", marker="D", linewidth=2.4, markersize=4.5, zorder=3)
    ax.set_xticks([0, 1], ["原发灶", "转移灶"])
    ax.set_ylabel(METRIC_LABELS.get(metric, metric))
    ax.set_title(title, fontsize=11)
    ax.grid(axis="y", linestyle="--", color=GRID_COLOR, alpha=0.65)
    p_value, _ = paired_wilcoxon(plot_df[d_col])
    annotate_pair_stats(ax, plot_df, d_col, p_value)


def make_metric_grid_figure(pair_metrics_df: pd.DataFrame, metrics: list[str], groups: list[str], out_path: Path, suptitle: str) -> None:
    fig, axes = plt.subplots(len(metrics), len(groups), figsize=(4.7 * len(groups), 3.5 * len(metrics)))
    if len(metrics) == 1 and len(groups) == 1:
        axes = np.array([[axes]])
    elif len(metrics) == 1:
        axes = np.array([axes])
    elif len(groups) == 1:
        axes = np.array([[ax] for ax in axes])

    for row_idx, metric in enumerate(metrics):
        for col_idx, group in enumerate(groups):
            ax = axes[row_idx, col_idx]
            sub_df = pair_metrics_df if group == "ALL" else pair_metrics_df[pair_metrics_df["group"] == group]
            draw_paired_lines(ax, sub_df, metric, f"{group}组 | {METRIC_LABELS.get(metric, metric)}")

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PRIMARY_COLOR, markersize=7, label="原发灶"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=MET_COLOR, markersize=7, label="转移灶"),
        Line2D([0], [0], color="#111111", marker="D", lw=2.2, label="组均值连线"),
    ]
    fig.suptitle(suptitle, fontsize=16, y=0.99)
    fig.legend(handles=legend_handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.96))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def make_significance_heatmap(significance_df: pd.DataFrame, out_path: Path) -> None:
    view_df = significance_df.copy()
    view_df["row_label"] = view_df["group"] + " | " + view_df["filter_name"]
    view_df["metric_label"] = view_df["metric"].str.replace("diff_", "", regex=False).map(lambda x: METRIC_LABELS.get(x, x))
    heat_df = view_df.pivot_table(index="row_label", columns="metric_label", values="wilcoxon_p", aggfunc="first")
    heat_df = heat_df[[col for col in heat_df.columns if col in [METRIC_LABELS[m.replace('diff_', '')] for m in SIGNIFICANCE_METRICS]]]

    fig, ax = plt.subplots(figsize=(12, 4.5))
    values = heat_df.to_numpy(dtype=float)
    im = ax.imshow(values, cmap="YlGnBu_r", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(np.arange(heat_df.shape[1]), heat_df.columns, rotation=25, ha="right")
    ax.set_yticks(np.arange(heat_df.shape[0]), heat_df.index)
    ax.set_title("配对显著性热图（Wilcoxon p 值）", fontsize=15)

    for row in range(heat_df.shape[0]):
        for col in range(heat_df.shape[1]):
            value = values[row, col]
            text = "NA" if pd.isna(value) else format_value(value, 4)
            ax.text(col, row, text, ha="center", va="center", color="#111111", fontsize=9)

    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def print_summary(significance_df: pd.DataFrame) -> None:
    print("\n===== 显著性结果（关键指标） =====")
    print(significance_df.to_string(index=False))

    print("\n===== 说明 =====")
    print("1. current baseline 口径保持不变：Tumor / M1 / M2 仍按 PanCK/CD68/CD86/CD163 的原规则重建。")
    print(f"2. 额外输出了一个低M1过滤版本：仅保留原发与转移都满足 M1_n >= {MIN_M1_THRESHOLD} 的 R 组配对。")
    print("3. 如果图上趋势明显但 p 值不小，通常是因为配对数少、方向不完全一致、或者存在低计数样本。")


def main() -> None:
    _, pair_manifest_df = preprocess_raw_samples()
    pair_metrics_df = build_pair_metrics(pair_manifest_df)
    significance_df = build_significance_table(pair_metrics_df)

    make_metric_grid_figure(
        pair_metrics_df,
        metrics=["m1_to_tumor", "enrich_20_Tumor_M1", "enrich_30_Tumor_M1"],
        groups=["R", "L", "QT"],
        out_path=OUT_DIR / "M1趋势指标_分组配对折线图.png",
        suptitle="M1趋势相关指标：按原始数据重建后的分组配对折线图",
    )
    make_metric_grid_figure(
        pair_metrics_df,
        metrics=["m2_dist_median", "within_20_M2", "within_30_M2"],
        groups=["R", "L", "QT", "ALL"],
        out_path=OUT_DIR / "M2空间指标_分组配对折线图.png",
        suptitle="M2空间位置相关指标：按原始数据重建后的分组配对折线图",
    )

    filtered_r_df = pair_metrics_df[
        (pair_metrics_df["group"] == "R")
        & (pair_metrics_df["primary_m1_n"] >= MIN_M1_THRESHOLD)
        & (pair_metrics_df["met_m1_n"] >= MIN_M1_THRESHOLD)
    ].copy()
    make_metric_grid_figure(
        filtered_r_df,
        metrics=["m1_to_tumor", "enrich_20_Tumor_M1", "enrich_30_Tumor_M1"],
        groups=["R"],
        out_path=OUT_DIR / "R组_低M1过滤后_M1趋势指标.png",
        suptitle=f"R组低M1过滤后（原发与转移均满足 M1_n >= {MIN_M1_THRESHOLD}）",
    )

    make_significance_heatmap(significance_df, OUT_DIR / "显著性热图.png")
    print_summary(significance_df)

    print("\n输出目录：")
    print(OUT_DIR)


if __name__ == "__main__":
    main()
