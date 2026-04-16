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
OUT_DIR = Path("/Users/jia/Desktop/学习 /毕业设计/实验/2轮/round2")

SAMPLE_TABLE = OUT_DIR / "sample_summary.tsv"
PAIR_TABLE = OUT_DIR / "pair_metrics.tsv"
SIG_TABLE = OUT_DIR / "significance_summary.tsv"

GRID_SIZE = 6
M1_THRESHOLDS = [0, 50, 100]

plt.rcParams["axes.unicode_minus"] = False
PRIMARY_COLOR = "#2B6CB0"
MET_COLOR = "#C53030"
ACCENT_COLOR = "#2F855A"
GRID_COLOR = "#D9D9D9"

KEY_METRICS = [
    "m1_n",
    "m2_n",
    "mac_n",
    "m1_density",
    "m2_density",
    "m1_to_tumor",
    "m2_to_tumor",
    "m1_dist_median",
    "m2_dist_median",
    "dist_gap_m2_minus_m1",
    "window_high_m2_frac",
    "window_high_m1_frac",
    "window_m2_outer_frac",
]

LABELS = {
    "m1_n": "M1数量",
    "m2_n": "M2数量",
    "mac_n": "巨噬细胞数量",
    "m1_density": "M1相对密度",
    "m2_density": "M2相对密度",
    "m1_to_tumor": "M1 / Tumor",
    "m2_to_tumor": "M2 / Tumor",
    "m1_dist_median": "M1到最近Tumor中位距离",
    "m2_dist_median": "M2到最近Tumor中位距离",
    "dist_gap_m2_minus_m1": "M2距离 - M1距离",
    "window_high_m2_frac": "高M2窗口占比",
    "window_high_m1_frac": "高M1窗口占比",
    "window_m2_outer_frac": "M2外围偏置窗口占比",
}


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


def detect_required_columns(columns: list[str]) -> dict[str, str | None]:
    col_map = {
        "cell_id": pick_col(columns, aliases=["objectid", "cellid", "id", "objectnumber"]),
        "x": pick_col(columns, aliases=["centerx", "centroidx", "xcenter", "positionx", "locationx", "xcoord", "coordx"]),
        "y": pick_col(columns, aliases=["centery", "centroidy", "ycenter", "positiony", "locationy", "ycoord", "coordy"]),
        "panck": pick_col(columns, aliases=["pancytokeratin", "panck"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["pancytokeratin", "panck"]),
        "cd68": pick_col(columns, aliases=["cd68"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd68"]),
        "cd86": pick_col(columns, aliases=["cd86"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd86"]),
        "cd163": pick_col(columns, aliases=["cd163"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd163"]),
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
    return sub[["Center X", "Center Y"]].to_numpy(dtype=float) if len(sub) else np.empty((0, 2), dtype=float)


def within_r_ratio(src_coords: np.ndarray, tgt_coords: np.ndarray, radius: float) -> float:
    if len(src_coords) == 0 or len(tgt_coords) == 0:
        return np.nan
    distances, _ = cKDTree(tgt_coords).query(src_coords, k=1)
    distances = np.asarray(distances, dtype=float)
    return float(np.mean(distances <= radius))


def median_nearest_distance(src_coords: np.ndarray, tgt_coords: np.ndarray) -> float:
    if len(src_coords) == 0 or len(tgt_coords) == 0:
        return np.nan
    distances, _ = cKDTree(tgt_coords).query(src_coords, k=1)
    distances = np.asarray(distances, dtype=float)
    distances = distances[np.isfinite(distances)]
    return float(np.median(distances)) if len(distances) else np.nan


def sample_area(coords: np.ndarray) -> float:
    if len(coords) == 0:
        return np.nan
    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)
    return max(max_x - min_x, 1.0) * max(max_y - min_y, 1.0)


def init_bucket() -> dict[str, int]:
    return {"Tumor": 0, "M1": 0, "M2": 0}


def compute_window_metrics(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {
            "window_high_m2_frac": np.nan,
            "window_high_m1_frac": np.nan,
            "window_m2_outer_frac": np.nan,
        }
    coords = df[["Center X", "Center Y"]].to_numpy(dtype=float)
    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)
    width = max(max_x - min_x, 1.0)
    height = max(max_y - min_y, 1.0)
    tmp = df.copy()
    tmp["row"] = np.minimum(((tmp["Center Y"] - min_y) / height * GRID_SIZE).astype(int), GRID_SIZE - 1)
    tmp["col"] = np.minimum(((tmp["Center X"] - min_x) / width * GRID_SIZE).astype(int), GRID_SIZE - 1)
    counts = (
        tmp.groupby(["row", "col", "cell_type"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=["Tumor", "M1", "M2"], fill_value=0)
        .reindex(pd.MultiIndex.from_product([range(GRID_SIZE), range(GRID_SIZE)], names=["row", "col"]), fill_value=0)
        .reset_index()
    )
    tumor = counts["Tumor"].to_numpy(dtype=float)
    m1 = counts["M1"].to_numpy(dtype=float)
    m2 = counts["M2"].to_numpy(dtype=float)
    mac = m1 + m2
    total = tumor + mac
    with np.errstate(divide="ignore", invalid="ignore"):
        m2_ratio = np.divide(m2, mac, out=np.full_like(m2, np.nan), where=mac > 0)
        m1_ratio = np.divide(m1, mac, out=np.full_like(m1, np.nan), where=mac > 0)
        m2_to_tumor = np.divide(m2, tumor, out=np.full_like(m2, np.nan), where=tumor > 0)
        tumor_density = np.divide(tumor, total, out=np.full_like(tumor, np.nan), where=total > 0)
    metric_df = pd.DataFrame(
        {
            "m2_ratio": m2_ratio,
            "m1_ratio": m1_ratio,
            "m2_to_tumor": m2_to_tumor,
            "tumor_density": tumor_density,
        }
    )
    high_m2 = ((metric_df["m2_ratio"] >= 0.7) & (metric_df["tumor_density"] >= 0.2)).mean()
    high_m1 = ((metric_df["m1_ratio"] >= 0.3) & (metric_df["tumor_density"] >= 0.2)).mean()
    outer = ((metric_df["m2_ratio"] >= 0.7) & (metric_df["m2_to_tumor"] <= 0.3)).mean()
    return {
        "window_high_m2_frac": float(high_m2),
        "window_high_m1_frac": float(high_m1),
        "window_m2_outer_frac": float(outer),
    }


def load_analysis_from_raw(objects_file: Path) -> pd.DataFrame:
    header_df = pd.read_csv(objects_file, sep="\t", nrows=0)
    col_map = detect_required_columns(list(header_df.columns))
    usecols = [col_map[key] for key in ["x", "y", "panck", "cd68", "cd86", "cd163"]]
    if col_map["cell_id"] is not None:
        usecols.append(col_map["cell_id"])
    usecols = list(dict.fromkeys(usecols))
    raw_df = pd.read_csv(objects_file, sep="\t", usecols=usecols, low_memory=False)
    cell_id = raw_df[col_map["cell_id"]] if col_map["cell_id"] is not None else pd.Series(np.arange(len(raw_df)), index=raw_df.index)
    clean = pd.DataFrame(
        {
            "cell_id": cell_id,
            "Center X": pd.to_numeric(raw_df[col_map["x"]], errors="coerce"),
            "Center Y": pd.to_numeric(raw_df[col_map["y"]], errors="coerce"),
            "PanCK": to_numeric_binary(raw_df[col_map["panck"]]),
            "CD68": to_numeric_binary(raw_df[col_map["cd68"]]),
            "CD86": to_numeric_binary(raw_df[col_map["cd86"]]),
            "CD163": to_numeric_binary(raw_df[col_map["cd163"]]),
        }
    )
    clean = clean.dropna(subset=["Center X", "Center Y"]).copy()
    clean["is_tumor"] = ((clean["PanCK"] == 1) & (clean["CD68"] == 0)).astype(np.int8)
    clean["is_mac"] = ((clean["CD68"] == 1) & (clean["PanCK"] == 0)).astype(np.int8)
    clean["is_m1"] = ((clean["CD68"] == 1) & (clean["CD86"] == 1) & (clean["CD163"] == 0) & (clean["PanCK"] == 0)).astype(np.int8)
    clean["is_m2"] = ((clean["CD68"] == 1) & (clean["CD163"] == 1) & (clean["CD86"] == 0) & (clean["PanCK"] == 0)).astype(np.int8)
    clean["is_ambiguous_mac"] = ((clean["CD68"] == 1) & (clean["CD86"] == 1) & (clean["CD163"] == 1) & (clean["PanCK"] == 0)).astype(np.int8)
    clean["cell_type"] = clean.apply(cell_type_from_flags, axis=1)
    return clean[clean["cell_type"].isin(["Tumor", "M1", "M2"])].copy()


def build_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sample_rows = []
    pair_index: dict[int, dict[str, dict[str, str]]] = {}

    for sample_dir in sorted([p for p in RAW_ROOT.iterdir() if p.is_dir()], key=lambda p: p.name):
        sample_name = sample_dir.name.strip()
        patient_id, suffix = parse_sample_name(sample_name)
        if patient_id is None or suffix not in {"P", "L", "R"}:
            continue
        objects_file = find_largest_objects_file(sample_dir)
        if objects_file is None:
            continue
        analysis_df = load_analysis_from_raw(objects_file)
        tumor_coords = get_coords(analysis_df, "Tumor")
        m1_coords = get_coords(analysis_df, "M1")
        m2_coords = get_coords(analysis_df, "M2")
        coords = analysis_df[["Center X", "Center Y"]].to_numpy(dtype=float)
        area = sample_area(coords)
        tumor_n = len(tumor_coords)
        m1_n = len(m1_coords)
        m2_n = len(m2_coords)
        mac_n = m1_n + m2_n
        m1_dist = median_nearest_distance(m1_coords, tumor_coords)
        m2_dist = median_nearest_distance(m2_coords, tumor_coords)
        window_metrics = compute_window_metrics(analysis_df)

        sample_rows.append(
            {
                "patient_id": patient_id,
                "sample_name": sample_name,
                "sample_suffix": suffix,
                "source_file": str(objects_file),
                "tumor_n": tumor_n,
                "m1_n": m1_n,
                "m2_n": m2_n,
                "mac_n": mac_n,
                "bbox_area": area,
                "m1_density": safe_div(m1_n * 1_000_000, area),
                "m2_density": safe_div(m2_n * 1_000_000, area),
                "mac_density": safe_div(mac_n * 1_000_000, area),
                "m1_to_tumor": safe_div(m1_n, tumor_n),
                "m2_to_tumor": safe_div(m2_n, tumor_n),
                "m1_frac_of_mac": safe_div(m1_n, mac_n),
                "m2_frac_of_mac": safe_div(m2_n, mac_n),
                "m1_dist_median": m1_dist,
                "m2_dist_median": m2_dist,
                "dist_gap_m2_minus_m1": m2_dist - m1_dist if pd.notna(m1_dist) and pd.notna(m2_dist) else np.nan,
                **window_metrics,
            }
        )
        pair_index.setdefault(patient_id, {})[suffix] = {"sample_name": sample_name, "source_file": str(objects_file)}

    sample_df = pd.DataFrame(sample_rows).sort_values(["patient_id", "sample_name"]).reset_index(drop=True)
    round_numeric(sample_df).to_csv(SAMPLE_TABLE, sep="\t", index=False)

    pair_rows = []
    for patient_id, samples in sorted(pair_index.items()):
        if "P" not in samples:
            continue
        for suffix in ["L", "R"]:
            if suffix not in samples:
                continue
            primary = sample_df[(sample_df["patient_id"] == patient_id) & (sample_df["sample_suffix"] == "P")].iloc[0]
            met = sample_df[(sample_df["patient_id"] == patient_id) & (sample_df["sample_suffix"] == suffix)].iloc[0]
            row = {
                "group": suffix,
                "patient_id": patient_id,
                "pair_label": f"{primary['sample_name']} vs {met['sample_name']}",
                "primary_sample": primary["sample_name"],
                "met_sample": met["sample_name"],
            }
            for metric in KEY_METRICS:
                row[f"primary_{metric}"] = primary[metric]
                row[f"met_{metric}"] = met[metric]
                row[f"diff_{metric}"] = met[metric] - primary[metric] if pd.notna(primary[metric]) and pd.notna(met[metric]) else np.nan
            pair_rows.append(row)
    pair_df = pd.DataFrame(pair_rows).sort_values(["group", "patient_id"]).reset_index(drop=True)
    round_numeric(pair_df).to_csv(PAIR_TABLE, sep="\t", index=False)
    return sample_df, pair_df


def paired_p(values: pd.Series) -> tuple[float, int]:
    x = values.dropna().to_numpy(dtype=float)
    if len(x) < 2:
        return np.nan, len(x)
    try:
        return float(wilcoxon(x, zero_method="pratt").pvalue), len(x)
    except Exception:
        return np.nan, len(x)


def build_significance(pair_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    subsets = [("ALL", pair_df), ("R", pair_df[pair_df["group"] == "R"]), ("L", pair_df[pair_df["group"] == "L"])]
    for group, sub_df in subsets:
        for threshold in M1_THRESHOLDS:
            if threshold == 0:
                filt_df = sub_df.copy()
                filter_name = "all_pairs"
            else:
                filt_df = sub_df[(sub_df["primary_m1_n"] >= threshold) & (sub_df["met_m1_n"] >= threshold)].copy()
                filter_name = f"m1_both_ge_{threshold}"
            for metric in KEY_METRICS:
                diff_col = f"diff_{metric}"
                p, n = paired_p(filt_df[diff_col])
                vals = filt_df[diff_col].dropna()
                rows.append(
                    {
                        "group": group,
                        "filter_name": filter_name,
                        "metric": metric,
                        "n_pairs": n,
                        "mean_diff": float(vals.mean()) if len(vals) else np.nan,
                        "median_diff": float(vals.median()) if len(vals) else np.nan,
                        "wilcoxon_p": p,
                    }
                )
    sig_df = round_numeric(pd.DataFrame(rows))
    sig_df.to_csv(SIG_TABLE, sep="\t", index=False)
    return sig_df


def annotate_stats(ax, vals: pd.Series, p_value: float) -> None:
    if vals.dropna().empty:
        text = "无有效配对"
    else:
        text = f"n={vals.dropna().shape[0]}\n平均差={format_value(vals.mean())}\np={format_value(p_value,4) if pd.notna(p_value) else 'NA'}"
    ax.text(
        0.03, 0.97, text, transform=ax.transAxes, ha="left", va="top",
        fontsize=8.5, color=ACCENT_COLOR,
        bbox={"facecolor": "white", "edgecolor": "#DDDDDD", "alpha": 0.9},
    )


def draw_pair_lines(ax, sub_df: pd.DataFrame, metric: str, title: str) -> None:
    p_col, m_col, d_col = f"primary_{metric}", f"met_{metric}", f"diff_{metric}"
    tmp = sub_df[["pair_label", p_col, m_col, d_col]].dropna().reset_index(drop=True)
    if tmp.empty:
        ax.axis("off")
        ax.set_title(title)
        return
    for _, row in tmp.iterrows():
        ax.plot([0, 1], [row[p_col], row[m_col]], color="#8A8A8A", linewidth=1.2, alpha=0.75)
        ax.scatter([0], [row[p_col]], color=PRIMARY_COLOR, s=34)
        ax.scatter([1], [row[m_col]], color=MET_COLOR, s=34)
    ax.plot([0, 1], [tmp[p_col].mean(), tmp[m_col].mean()], color="#111111", marker="D", linewidth=2.2, markersize=4.5)
    ax.set_xticks([0, 1], ["原发灶", "转移灶"])
    ax.set_title(title, fontsize=11)
    ax.set_ylabel(LABELS.get(metric, metric))
    ax.grid(axis="y", linestyle="--", color=GRID_COLOR, alpha=0.65)
    p, _ = paired_p(tmp[d_col])
    annotate_stats(ax, tmp[d_col], p)


def make_line_grid(pair_df: pd.DataFrame, metrics: list[str], groups: list[str], out_path: Path, suptitle: str) -> None:
    fig, axes = plt.subplots(len(metrics), len(groups), figsize=(4.6 * len(groups), 3.4 * len(metrics)))
    if len(metrics) == 1 and len(groups) == 1:
        axes = np.array([[axes]])
    elif len(metrics) == 1:
        axes = np.array([axes])
    elif len(groups) == 1:
        axes = np.array([[ax] for ax in axes])
    for i, metric in enumerate(metrics):
        for j, group in enumerate(groups):
            sub = pair_df if group == "ALL" else pair_df[pair_df["group"] == group]
            draw_pair_lines(axes[i, j], sub, metric, f"{group}组 | {LABELS.get(metric, metric)}")
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PRIMARY_COLOR, markersize=7, label="原发灶"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=MET_COLOR, markersize=7, label="转移灶"),
        Line2D([0], [0], color="#111111", marker="D", lw=2.2, label="组均值"),
    ]
    fig.suptitle(suptitle, fontsize=16, y=0.99)
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.96))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def make_threshold_bar(sig_df: pd.DataFrame, metric: str, out_path: Path) -> None:
    plot_df = sig_df[(sig_df["group"].isin(["ALL", "R", "L"])) & (sig_df["metric"] == metric)].copy()
    pivot = plot_df.pivot(index="filter_name", columns="group", values="wilcoxon_p").reindex(
        ["all_pairs", "m1_both_ge_50", "m1_both_ge_100"]
    )
    x = np.arange(len(pivot.index))
    width = 0.24
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for idx, group in enumerate(["ALL", "R", "L"]):
        vals = pivot[group].to_numpy(dtype=float)
        bars = ax.bar(x + (idx - 1) * width, vals, width=width, label=f"{group}组")
        for rect, val in zip(bars, vals):
            ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 0.02 if pd.notna(val) else 0.02,
                    format_value(val, 4) if pd.notna(val) else "NA", ha="center", va="bottom", fontsize=8.5)
    ax.axhline(0.05, color="#444444", linestyle="--", linewidth=1.0)
    ax.set_xticks(x, ["全部", "M1>=50", "M1>=100"])
    ax.set_ylabel("Wilcoxon p 值")
    ax.set_ylim(0, 1.05)
    ax.set_title(f"低M1阈值稳健性：{LABELS.get(metric, metric)}", fontsize=14)
    ax.legend(frameon=False)
    ax.grid(axis="y", linestyle="--", color=GRID_COLOR, alpha=0.65)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def make_sig_heatmap(sig_df: pd.DataFrame, metrics: list[str], out_path: Path) -> None:
    sub = sig_df[sig_df["filter_name"] == "all_pairs"].copy()
    sub["row"] = sub["group"]
    sub["col"] = sub["metric"].map(lambda x: LABELS.get(x, x))
    heat = sub.pivot(index="row", columns="col", values="wilcoxon_p").reindex(index=["ALL", "R", "L"])
    heat = heat[[LABELS[m] for m in metrics]]
    vals = heat.to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    im = ax.imshow(vals, cmap="YlGnBu_r", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(np.arange(heat.shape[1]), heat.columns, rotation=20, ha="right")
    ax.set_yticks(np.arange(heat.shape[0]), heat.index)
    ax.set_title("all_pairs 显著性热图", fontsize=14)
    for r in range(heat.shape[0]):
        for c in range(heat.shape[1]):
            v = vals[r, c]
            ax.text(c, r, format_value(v, 4) if pd.notna(v) else "NA", ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def report_conclusions(sig_df: pd.DataFrame) -> None:
    print("\n===== 可关注的显著性结果 =====")
    sub = sig_df[(sig_df["filter_name"] == "all_pairs") & (sig_df["group"].isin(["ALL", "R", "L"]))].copy()
    sub = sub.sort_values(["wilcoxon_p", "group", "metric"])
    print(sub.head(20).to_string(index=False))
    print("\n===== 输出目录 =====")
    print(OUT_DIR)


def main() -> None:
    build_data()
    pair_df = pd.read_csv(PAIR_TABLE, sep="\t")
    sig_df = build_significance(pair_df)

    make_line_grid(pair_df, ["m1_n", "m2_n", "mac_n"], ["ALL", "R", "L"], OUT_DIR / "01_数量折线图.png", "数量维度")
    make_line_grid(pair_df, ["m1_density", "m2_density", "m2_to_tumor"], ["ALL", "R", "L"], OUT_DIR / "02_密度与比例折线图.png", "密度与Tumor归一化比例")
    make_line_grid(pair_df, ["m1_dist_median", "m2_dist_median", "dist_gap_m2_minus_m1"], ["ALL", "R", "L"], OUT_DIR / "03_距离分布折线图.png", "距离分布维度")
    make_line_grid(pair_df, ["window_high_m2_frac", "window_high_m1_frac", "window_m2_outer_frac"], ["ALL", "R", "L"], OUT_DIR / "04_局部窗口折线图.png", "局部窗口维度")
    make_line_grid(pair_df, ["m1_to_tumor", "m2_to_tumor"], ["ALL", "R", "L"], OUT_DIR / "05_Tumor归一化折线图.png", "Tumor归一化指标")

    make_threshold_bar(sig_df, "m2_to_tumor", OUT_DIR / "06_低M1阈值_M2toTumor柱状图.png")
    make_threshold_bar(sig_df, "m1_to_tumor", OUT_DIR / "07_低M1阈值_M1toTumor柱状图.png")
    make_sig_heatmap(sig_df, ["m1_to_tumor", "m2_to_tumor", "m2_dist_median", "window_m2_outer_frac", "m1_density", "m2_density"], OUT_DIR / "08_显著性热图.png")

    report_conclusions(sig_df)


if __name__ == "__main__":
    main()
