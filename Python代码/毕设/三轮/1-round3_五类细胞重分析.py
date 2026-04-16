from pathlib import Path
import re
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree
from scipy.stats import wilcoxon


RAW_ROOT = Path("/Users/jia/Desktop/学习 /毕业设计/实验/CODEX全部分析数据-20260116")
OUT_DIR = Path("/Users/jia/Desktop/学习 /毕业设计/实验/3轮/round3")

SAMPLE_TABLE = OUT_DIR / "sample_summary.tsv"
PAIR_TABLE = OUT_DIR / "pair_metrics.tsv"
SIG_TABLE = OUT_DIR / "significance_summary.tsv"
SENS_TABLE = OUT_DIR / "cd8_extreme_sensitivity.tsv"
LEAVE_ONE_OUT_TABLE = OUT_DIR / "cd8_leave_one_out.tsv"
REPORT_SUMMARY = OUT_DIR / "10_第三轮主线汇报总结.md"

GRID_SIZE = 6

PRIMARY_COLOR = "#2B6CB0"
MET_COLOR = "#C53030"
ACCENT_COLOR = "#2F855A"
GRID_COLOR = "#D9D9D9"

PLOT_METRICS = [
    "Macrophage_n",
    "M2_like_Macrophage_n",
    "CD8_T_n",
    "Stromal_n",
    "PYCR1_Stromal_n",
    "Macrophage_density",
    "M2_like_Macrophage_density",
    "CD8_T_density",
    "Stromal_density",
    "PYCR1_Stromal_density",
    "M2_like_Macrophage_to_tumor",
    "CD8_T_to_tumor",
    "Stromal_to_tumor",
    "PYCR1_Stromal_to_tumor",
    "M2_like_Macrophage_dist_to_tumor",
    "CD8_T_dist_to_tumor",
    "Stromal_dist_to_tumor",
    "PYCR1_Stromal_dist_to_tumor",
    "M2_like_Macrophage_dist_to_stromal",
    "CD8_T_dist_to_stromal",
    "PYCR1_Stromal_dist_to_cd8",
    "CD8_T_dist_to_PYCR1_Stromal",
    "window_m2_stromal_frac",
    "window_cd8_tumor_frac",
    "window_tumor_stromal_frac",
]

LABELS = {
    "Macrophage_n": "巨噬细胞数量",
    "M2_like_Macrophage_n": "M2样巨噬细胞数量",
    "CD8_T_n": "CD8阳性T细胞数量",
    "Stromal_n": "基质细胞数量",
    "PYCR1_Stromal_n": "PYCR1阳性基质细胞数量",
    "Macrophage_density": "巨噬细胞相对密度",
    "M2_like_Macrophage_density": "M2样巨噬细胞相对密度",
    "CD8_T_density": "CD8阳性T细胞相对密度",
    "Stromal_density": "基质细胞相对密度",
    "PYCR1_Stromal_density": "PYCR1阳性基质细胞相对密度",
    "M2_like_Macrophage_to_tumor": "M2样巨噬细胞 / 肿瘤",
    "CD8_T_to_tumor": "CD8阳性T细胞 / 肿瘤",
    "Stromal_to_tumor": "基质细胞 / 肿瘤",
    "PYCR1_Stromal_to_tumor": "PYCR1阳性基质细胞 / 肿瘤",
    "M2_like_Macrophage_dist_to_tumor": "M2样巨噬细胞到Tumor中位距离",
    "CD8_T_dist_to_tumor": "CD8阳性T细胞到Tumor中位距离",
    "Stromal_dist_to_tumor": "基质细胞到Tumor中位距离",
    "PYCR1_Stromal_dist_to_tumor": "PYCR1阳性基质细胞到Tumor中位距离",
    "M2_like_Macrophage_dist_to_stromal": "M2样巨噬细胞到基质中位距离",
    "CD8_T_dist_to_stromal": "CD8阳性T细胞到基质中位距离",
    "PYCR1_Stromal_dist_to_cd8": "PYCR1阳性基质细胞到CD8中位距离",
    "CD8_T_dist_to_PYCR1_Stromal": "CD8阳性T细胞到PYCR1阳性基质中位距离",
    "window_m2_stromal_frac": "M2样+基质共富集窗口占比",
    "window_cd8_tumor_frac": "CD8+肿瘤共富集窗口占比",
    "window_tumor_stromal_frac": "肿瘤+基质共富集窗口占比",
}

CD8_METRICS = ["CD8_T_n", "CD8_T_density", "CD8_T_to_tumor"]


def norm_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text).lower())


def format_value(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def round_numeric(df: pd.DataFrame, digits: int = 2) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]):
            out[col] = out[col].round(digits)
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
        "cd3e": pick_col(columns, aliases=["cd3e"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd3e"]),
        "cd8": pick_col(columns, aliases=["cd8"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd8"]),
        "sma": pick_col(columns, aliases=["sma"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["sma"]),
        "vimentin": pick_col(columns, aliases=["vimentin"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["vimentin"]),
        "cd31": pick_col(columns, aliases=["cd31"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd31"]),
        "pycr1": pick_col(columns, aliases=["pycr1"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["pycr1"]),
    }
    missing = [key for key, value in col_map.items() if key not in {"cell_id"} and value is None]
    if missing:
        raise ValueError(f"缺少关键列：{missing}")
    return col_map


def to_binary(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    return (values > 0.5).astype(np.int8)


def safe_div(a: float, b: float) -> float:
    if b == 0 or pd.isna(b):
        return np.nan
    return float(a) / float(b)


def get_coords(df: pd.DataFrame, flag_col: str) -> np.ndarray:
    sub = df[df[flag_col] == 1]
    return sub[["Center X", "Center Y"]].to_numpy(dtype=float) if len(sub) else np.empty((0, 2), dtype=float)


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


def compute_window_metrics(df: pd.DataFrame) -> dict[str, float]:
    coords = df[["Center X", "Center Y"]].to_numpy(dtype=float)
    if len(coords) == 0:
        return {"window_m2_stromal_frac": np.nan, "window_cd8_tumor_frac": np.nan, "window_tumor_stromal_frac": np.nan}
    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)
    width = max(max_x - min_x, 1.0)
    height = max(max_y - min_y, 1.0)
    tmp = df.copy()
    tmp["row"] = np.minimum(((tmp["Center Y"] - min_y) / height * GRID_SIZE).astype(int), GRID_SIZE - 1)
    tmp["col"] = np.minimum(((tmp["Center X"] - min_x) / width * GRID_SIZE).astype(int), GRID_SIZE - 1)
    count_cols = ["is_tumor", "is_macrophage", "is_m2_like_macrophage", "is_cd8_t", "is_stromal"]
    grouped = tmp.groupby(["row", "col"])[count_cols].sum().reindex(
        pd.MultiIndex.from_product([range(GRID_SIZE), range(GRID_SIZE)], names=["row", "col"]),
        fill_value=0,
    ).reset_index()
    tumor = grouped["is_tumor"].to_numpy(dtype=float)
    m2 = grouped["is_m2_like_macrophage"].to_numpy(dtype=float)
    cd8 = grouped["is_cd8_t"].to_numpy(dtype=float)
    stromal = grouped["is_stromal"].to_numpy(dtype=float)
    total = tumor + m2 + cd8 + stromal
    with np.errstate(divide="ignore", invalid="ignore"):
        tumor_density = np.divide(tumor, total, out=np.full_like(tumor, np.nan), where=total > 0)
        stromal_density = np.divide(stromal, total, out=np.full_like(stromal, np.nan), where=total > 0)
        m2_density = np.divide(m2, total, out=np.full_like(m2, np.nan), where=total > 0)
        cd8_density = np.divide(cd8, total, out=np.full_like(cd8, np.nan), where=total > 0)
    return {
        "window_m2_stromal_frac": float(((m2_density >= 0.2) & (stromal_density >= 0.2)).mean()),
        "window_cd8_tumor_frac": float(((cd8_density >= 0.15) & (tumor_density >= 0.2)).mean()),
        "window_tumor_stromal_frac": float(((tumor_density >= 0.2) & (stromal_density >= 0.2)).mean()),
    }


def load_sample_from_raw(objects_file: Path) -> pd.DataFrame:
    header_df = pd.read_csv(objects_file, sep="\t", nrows=0)
    col_map = detect_required_columns(list(header_df.columns))
    usecols = [col_map[key] for key in ["x", "y", "panck", "cd68", "cd86", "cd163", "cd3e", "cd8", "sma", "vimentin", "cd31", "pycr1"]]
    if col_map["cell_id"] is not None:
        usecols.append(col_map["cell_id"])
    usecols = list(dict.fromkeys(usecols))
    raw_df = pd.read_csv(objects_file, sep="\t", usecols=usecols, low_memory=False)
    cell_id = raw_df[col_map["cell_id"]] if col_map["cell_id"] is not None else pd.Series(np.arange(len(raw_df)), index=raw_df.index)
    df = pd.DataFrame(
        {
            "cell_id": cell_id,
            "Center X": pd.to_numeric(raw_df[col_map["x"]], errors="coerce"),
            "Center Y": pd.to_numeric(raw_df[col_map["y"]], errors="coerce"),
            "PanCK": to_binary(raw_df[col_map["panck"]]),
            "CD68": to_binary(raw_df[col_map["cd68"]]),
            "CD86": to_binary(raw_df[col_map["cd86"]]),
            "CD163": to_binary(raw_df[col_map["cd163"]]),
            "CD3e": to_binary(raw_df[col_map["cd3e"]]),
            "CD8": to_binary(raw_df[col_map["cd8"]]),
            "SMA": to_binary(raw_df[col_map["sma"]]),
            "Vimentin": to_binary(raw_df[col_map["vimentin"]]),
            "CD31": to_binary(raw_df[col_map["cd31"]]),
            "PYCR1": to_binary(raw_df[col_map["pycr1"]]),
        }
    )
    df = df.dropna(subset=["Center X", "Center Y"]).copy()
    df["is_tumor"] = (df["PanCK"] == 1).astype(np.int8)
    df["is_macrophage"] = ((df["CD68"] == 1) & (df["PanCK"] == 0)).astype(np.int8)
    df["is_m2_like_macrophage"] = ((df["CD68"] == 1) & (df["CD163"] == 1) & (df["PanCK"] == 0)).astype(np.int8)
    df["is_cd8_t"] = ((df["CD3e"] == 1) & (df["CD8"] == 1) & (df["PanCK"] == 0)).astype(np.int8)
    df["is_stromal"] = (((df["SMA"] == 1) | (df["Vimentin"] == 1)) & (df["CD31"] == 0) & (df["PanCK"] == 0)).astype(np.int8)
    df["is_pycr1_stromal"] = ((df["PYCR1"] == 1) & (df["is_stromal"] == 1)).astype(np.int8)
    return df


def compute_sample_metrics(df: pd.DataFrame) -> dict[str, float]:
    coords = df[["Center X", "Center Y"]].to_numpy(dtype=float)
    area = sample_area(coords)
    tumor_coords = get_coords(df, "is_tumor")
    stromal_coords = get_coords(df, "is_stromal")
    cd8_coords = get_coords(df, "is_cd8_t")
    pycr1_stromal_coords = get_coords(df, "is_pycr1_stromal")

    metrics = {"bbox_area": area}
    for key, flag_col in [
        ("Tumor", "is_tumor"),
        ("Macrophage", "is_macrophage"),
        ("M2_like_Macrophage", "is_m2_like_macrophage"),
        ("CD8_T", "is_cd8_t"),
        ("Stromal", "is_stromal"),
        ("PYCR1_Stromal", "is_pycr1_stromal"),
    ]:
        cell_coords = get_coords(df, flag_col)
        n = len(cell_coords)
        metrics[f"{key}_n"] = n
        metrics[f"{key}_density"] = safe_div(n * 1_000_000, area)
        if key != "Tumor":
            metrics[f"{key}_to_tumor"] = safe_div(n, len(tumor_coords))
            metrics[f"{key}_dist_to_tumor"] = median_nearest_distance(cell_coords, tumor_coords)
        if key in {"M2_like_Macrophage", "CD8_T"}:
            metrics[f"{key}_dist_to_stromal"] = median_nearest_distance(cell_coords, stromal_coords)
        if key == "PYCR1_Stromal":
            metrics[f"{key}_dist_to_cd8"] = median_nearest_distance(cell_coords, cd8_coords)
    metrics["CD8_T_dist_to_PYCR1_Stromal"] = median_nearest_distance(cd8_coords, pycr1_stromal_coords)
    metrics.update(compute_window_metrics(df))
    return metrics


def build_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sample_rows = []
    sample_index = {}
    for sample_dir in sorted([p for p in RAW_ROOT.iterdir() if p.is_dir()], key=lambda p: p.name):
        sample_name = sample_dir.name.strip()
        patient_id, suffix = parse_sample_name(sample_name)
        if patient_id is None or suffix not in {"P", "L", "R"}:
            continue
        objects_file = find_largest_objects_file(sample_dir)
        if objects_file is None:
            continue
        df = load_sample_from_raw(objects_file)
        metrics = compute_sample_metrics(df)
        row = {
            "patient_id": patient_id,
            "sample_name": sample_name,
            "sample_suffix": suffix,
            "is_ovarian_met": int(suffix in {"L", "R"}),
            "source_file": str(objects_file),
            **metrics,
        }
        sample_rows.append(row)
        sample_index[(patient_id, suffix)] = row

    sample_df = pd.DataFrame(sample_rows).sort_values(["patient_id", "sample_name"]).reset_index(drop=True)
    round_numeric(sample_df).to_csv(SAMPLE_TABLE, sep="\t", index=False)

    pair_rows = []
    for patient_id in sorted(sample_df["patient_id"].unique()):
        if (patient_id, "P") not in sample_index:
            continue
        primary = sample_index[(patient_id, "P")]
        for suffix in ["R", "L"]:
            if (patient_id, suffix) not in sample_index:
                continue
            met = sample_index[(patient_id, suffix)]
            row = {
                "patient_id": patient_id,
                "pair_label": f"{primary['sample_name']} vs {met['sample_name']}",
                "primary_sample": primary["sample_name"],
                "met_sample": met["sample_name"],
                "met_suffix": suffix,
            }
            for metric in PLOT_METRICS:
                p_val = primary.get(metric, np.nan)
                m_val = met.get(metric, np.nan)
                row[f"primary_{metric}"] = p_val
                row[f"met_{metric}"] = m_val
                row[f"diff_{metric}"] = m_val - p_val if pd.notna(p_val) and pd.notna(m_val) else np.nan
            pair_rows.append(row)

    pair_df = pd.DataFrame(pair_rows).sort_values(["patient_id", "met_suffix"]).reset_index(drop=True)
    round_numeric(pair_df).to_csv(PAIR_TABLE, sep="\t", index=False)
    return sample_df, pair_df


def paired_p(values: pd.Series) -> tuple[float, int]:
    x = values.dropna().to_numpy(dtype=float)
    if len(x) < 2:
        return np.nan, len(x)
    if np.allclose(x, 0):
        return 1.0, len(x)
    try:
        return float(wilcoxon(x, zero_method="pratt").pvalue), len(x)
    except Exception:
        return np.nan, len(x)


def build_significance(pair_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in PLOT_METRICS:
        diff_col = f"diff_{metric}"
        p, n = paired_p(pair_df[diff_col])
        vals = pair_df[diff_col].dropna()
        rows.append(
            {
                "group": "ALL",
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


def iqr_bounds(values: pd.Series) -> tuple[float, float]:
    x = values.dropna().to_numpy(dtype=float)
    if len(x) < 4:
        return np.nan, np.nan
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def build_cd8_sensitivity(pair_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sens_rows = []
    loo_rows = []
    for metric in CD8_METRICS:
        diff_col = f"diff_{metric}"
        vals = pair_df[diff_col]
        full_p, full_n = paired_p(vals)
        lower, upper = iqr_bounds(vals)
        is_extreme = vals.lt(lower) | vals.gt(upper) if pd.notna(lower) else pd.Series(False, index=pair_df.index)
        extreme_pairs = pair_df.loc[is_extreme, "pair_label"].tolist()
        trimmed = pair_df.loc[~is_extreme].copy()
        trimmed_p, trimmed_n = paired_p(trimmed[diff_col])
        sens_rows.append(
            {
                "metric": metric,
                "full_n": full_n,
                "full_mean_diff": float(vals.dropna().mean()) if vals.dropna().shape[0] else np.nan,
                "full_p": full_p,
                "iqr_lower": lower,
                "iqr_upper": upper,
                "n_extreme_pairs": int(is_extreme.sum()),
                "extreme_pairs": "；".join(extreme_pairs) if extreme_pairs else "无",
                "trimmed_n": trimmed_n,
                "trimmed_mean_diff": float(trimmed[diff_col].dropna().mean()) if trimmed[diff_col].dropna().shape[0] else np.nan,
                "trimmed_p": trimmed_p,
            }
        )
        for idx, row in pair_df.iterrows():
            sub = pair_df.drop(index=idx)
            p_val, n_val = paired_p(sub[diff_col])
            loo_rows.append(
                {
                    "metric": metric,
                    "removed_pair": row["pair_label"],
                    "removed_met_suffix": row["met_suffix"],
                    "remaining_n": n_val,
                    "mean_diff_after_removal": float(sub[diff_col].dropna().mean()) if sub[diff_col].dropna().shape[0] else np.nan,
                    "p_after_removal": p_val,
                }
            )
    sens_df = round_numeric(pd.DataFrame(sens_rows))
    loo_df = round_numeric(pd.DataFrame(loo_rows), digits=4)
    sens_df.to_csv(SENS_TABLE, sep="\t", index=False)
    loo_df.to_csv(LEAVE_ONE_OUT_TABLE, sep="\t", index=False)
    return sens_df, loo_df


def annotate_stats(ax, vals: pd.Series, p_value: float) -> None:
    if vals.dropna().empty:
        text = "无有效配对"
    else:
        text = f"n={vals.dropna().shape[0]}\n平均差={format_value(vals.mean())}\np={format_value(p_value, 4) if pd.notna(p_value) else 'NA'}"
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


def draw_pair_lines(ax, pair_df: pd.DataFrame, metric: str, title: str) -> None:
    p_col, m_col, d_col = f"primary_{metric}", f"met_{metric}", f"diff_{metric}"
    tmp = pair_df[["pair_label", p_col, m_col, d_col]].dropna().reset_index(drop=True)
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


def make_line_grid(pair_df: pd.DataFrame, metrics: list[str], out_path: Path, suptitle: str) -> None:
    fig, axes = plt.subplots(len(metrics), 1, figsize=(6.0, 3.6 * len(metrics)))
    if len(metrics) == 1:
        axes = np.array([axes])
    for i, metric in enumerate(metrics):
        draw_pair_lines(axes[i], pair_df, metric, LABELS.get(metric, metric))
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=PRIMARY_COLOR, markersize=7, label="原发灶"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=MET_COLOR, markersize=7, label="转移灶"),
        Line2D([0], [0], color="#111111", marker="D", lw=2.2, label="组均值"),
    ]
    fig.suptitle(suptitle, fontsize=15, y=0.995)
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 0.975))
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def make_heatmap(sig_df: pd.DataFrame, metrics: list[str], out_path: Path) -> None:
    heat = sig_df.set_index("metric").reindex(metrics)[["wilcoxon_p"]]
    vals = heat.to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(5.5, max(4.0, 0.48 * len(metrics))))
    im = ax.imshow(vals, cmap="YlGnBu_r", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks([0], ["P值"])
    ax.set_yticks(np.arange(len(metrics)), [LABELS.get(m, m) for m in metrics])
    ax.set_title("第三轮显著性热图", fontsize=14)
    for r in range(len(metrics)):
        v = vals[r, 0]
        ax.text(0, r, format_value(v, 4) if pd.notna(v) else "NA", ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def make_cd8_sensitivity_plot(pair_df: pd.DataFrame, sens_df: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(3, 2, figsize=(11.5, 10.0))
    for i, metric in enumerate(CD8_METRICS):
        diff_col = f"diff_{metric}"
        tmp = pair_df[["pair_label", diff_col]].dropna().reset_index(drop=True)
        vals = tmp[diff_col]
        lower, upper = iqr_bounds(vals)
        is_extreme = vals.lt(lower) | vals.gt(upper) if pd.notna(lower) else pd.Series(False, index=vals.index)

        ax = axes[i, 0]
        bars = ax.bar(np.arange(len(vals)), vals, color=["#D97706" if flag else "#4A5568" for flag in is_extreme])
        ax.axhline(0, color="#999999", lw=0.8)
        if pd.notna(lower):
            ax.axhline(lower, color="#DD6B20", lw=1.0, ls="--")
            ax.axhline(upper, color="#DD6B20", lw=1.0, ls="--")
        ax.set_title(f"{LABELS[metric]} 差值分布")
        ax.set_ylabel("转移灶 - 原发灶")
        ax.set_xticks(np.arange(len(vals)), tmp["pair_label"], rotation=45, ha="right")

        ax2 = axes[i, 1]
        row = sens_df[sens_df["metric"] == metric].iloc[0]
        labels = ["原始", "去极值后"]
        p_values = [row["full_p"], row["trimmed_p"]]
        mean_diffs = [row["full_mean_diff"], row["trimmed_mean_diff"]]
        ax2.bar(labels, p_values, color=["#2B6CB0", "#2F855A"])
        ax2.axhline(0.05, color="#C53030", ls="--", lw=1.0)
        for x, (p_val, mean_diff) in enumerate(zip(p_values, mean_diffs)):
            ax2.text(x, p_val + 0.03 if pd.notna(p_val) else 0.03, f"p={format_value(p_val,4)}\n差值={format_value(mean_diff)}", ha="center", va="bottom", fontsize=8)
        ax2.set_ylim(0, 1.05)
        ax2.set_title(f"{LABELS[metric]} 极值敏感性")
        ax2.set_ylabel("Wilcoxon P值")
    fig.suptitle("CD8阳性T细胞极值敏感性分析", fontsize=15, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def get_sig_row(sig_df: pd.DataFrame, metric: str) -> pd.Series:
    row = sig_df[sig_df["metric"] == metric]
    if row.empty:
        raise KeyError(f"未找到指标：{metric}")
    return row.iloc[0]


def write_report_summary(sig_df: pd.DataFrame) -> None:
    cd8_n = get_sig_row(sig_df, "CD8_T_n")
    cd8_density = get_sig_row(sig_df, "CD8_T_density")
    cd8_to_tumor = get_sig_row(sig_df, "CD8_T_to_tumor")
    cd8_dist_to_tumor = get_sig_row(sig_df, "CD8_T_dist_to_tumor")
    stromal_n = get_sig_row(sig_df, "Stromal_n")
    stromal_density = get_sig_row(sig_df, "Stromal_density")
    stromal_to_tumor = get_sig_row(sig_df, "Stromal_to_tumor")
    stromal_dist_to_tumor = get_sig_row(sig_df, "Stromal_dist_to_tumor")
    cd8_dist_to_stromal = get_sig_row(sig_df, "CD8_T_dist_to_stromal")
    pycr1_stromal_n = get_sig_row(sig_df, "PYCR1_Stromal_n")
    pycr1_stromal_density = get_sig_row(sig_df, "PYCR1_Stromal_density")
    pycr1_stromal_to_tumor = get_sig_row(sig_df, "PYCR1_Stromal_to_tumor")
    pycr1_stromal_dist_to_tumor = get_sig_row(sig_df, "PYCR1_Stromal_dist_to_tumor")
    pycr1_stromal_dist_to_cd8 = get_sig_row(sig_df, "PYCR1_Stromal_dist_to_cd8")
    cd8_dist_to_pycr1_stromal = get_sig_row(sig_df, "CD8_T_dist_to_PYCR1_Stromal")

    lines = [
        "# 第三轮主线汇报总结",
        "",
        "## 当前最稳的主线结论",
        "",
        "当前最稳定、最适合继续作为主线汇报的结果仍然是 `CD8阳性T细胞下降`。",
        "",
        f"- `CD8_T_n`: n_pairs={int(cd8_n['n_pairs'])}, mean_diff={format_value(cd8_n['mean_diff'])}, median_diff={format_value(cd8_n['median_diff'])}, p={format_value(cd8_n['wilcoxon_p'], 4)}",
        f"- `CD8_T_density`: n_pairs={int(cd8_density['n_pairs'])}, mean_diff={format_value(cd8_density['mean_diff'])}, median_diff={format_value(cd8_density['median_diff'])}, p={format_value(cd8_density['wilcoxon_p'], 4)}",
        f"- `CD8_T_to_tumor`: n_pairs={int(cd8_to_tumor['n_pairs'])}, mean_diff={format_value(cd8_to_tumor['mean_diff'])}, median_diff={format_value(cd8_to_tumor['median_diff'])}, p={format_value(cd8_to_tumor['wilcoxon_p'], 4)}",
        "",
        "通俗解释：卵巢转移灶里不仅 `CD8+T` 总数更少，而且同样空间内更稀，相对于肿瘤细胞也更弱，因此可以较稳地提示转移灶抗肿瘤免疫减弱。",
        "",
        "## 第二步：CD8 到 Tumor 的距离",
        "",
        f"- `CD8_T_dist_to_tumor`: n_pairs={int(cd8_dist_to_tumor['n_pairs'])}, mean_diff={format_value(cd8_dist_to_tumor['mean_diff'])}, median_diff={format_value(cd8_dist_to_tumor['median_diff'])}, p={format_value(cd8_dist_to_tumor['wilcoxon_p'], 4)}",
        "",
        "解释：差值方向是正的，说明转移灶中的 `CD8` 有“更远离肿瘤”的方向性趋势，但当前 `p` 值不显著，不能把它写成已经被稳定证明的结论。",
        "",
        "## 第三步：Stromal 与 CD8/Tumor 的关系",
        "",
        f"- `Stromal_n`: n_pairs={int(stromal_n['n_pairs'])}, mean_diff={format_value(stromal_n['mean_diff'])}, median_diff={format_value(stromal_n['median_diff'])}, p={format_value(stromal_n['wilcoxon_p'], 4)}",
        f"- `Stromal_density`: n_pairs={int(stromal_density['n_pairs'])}, mean_diff={format_value(stromal_density['mean_diff'])}, median_diff={format_value(stromal_density['median_diff'])}, p={format_value(stromal_density['wilcoxon_p'], 4)}",
        f"- `Stromal_to_tumor`: n_pairs={int(stromal_to_tumor['n_pairs'])}, mean_diff={format_value(stromal_to_tumor['mean_diff'])}, median_diff={format_value(stromal_to_tumor['median_diff'])}, p={format_value(stromal_to_tumor['wilcoxon_p'], 4)}",
        f"- `Stromal_dist_to_tumor`: n_pairs={int(stromal_dist_to_tumor['n_pairs'])}, mean_diff={format_value(stromal_dist_to_tumor['mean_diff'])}, median_diff={format_value(stromal_dist_to_tumor['median_diff'])}, p={format_value(stromal_dist_to_tumor['wilcoxon_p'], 4)}",
        f"- `CD8_T_dist_to_stromal`: n_pairs={int(cd8_dist_to_stromal['n_pairs'])}, mean_diff={format_value(cd8_dist_to_stromal['mean_diff'])}, median_diff={format_value(cd8_dist_to_stromal['median_diff'])}, p={format_value(cd8_dist_to_stromal['wilcoxon_p'], 4)}",
        "",
        "解释：`Stromal_n` 在转移灶中有上升趋势，但没有达到显著；其余几个关键环节也都没有显著。因此当前还不能说已经形成了“基质增强、靠近肿瘤、把 CD8 隔在外面”的完整证据链。",
        "",
        "## 现在可以怎么讲",
        "",
        "可以讲：",
        "",
        "- 第三轮主线已经从原始数据中找到较稳定结果，核心是 `CD8+T` 在卵巢转移灶中下降。",
        "- 对 CD8 的进一步空间分析提示，它可能有远离肿瘤的趋势，但这一点目前只是方向性现象。",
        "- 对大类基质的分析没有形成完整显著链条，因此“基质屏障”目前仍是后续解释方向，而不是已经证明的机制。",
        "",
        "## 细分基质：PYCR1阳性基质亚群",
        "",
        f"- `PYCR1_Stromal_n`: n_pairs={int(pycr1_stromal_n['n_pairs'])}, mean_diff={format_value(pycr1_stromal_n['mean_diff'])}, median_diff={format_value(pycr1_stromal_n['median_diff'])}, p={format_value(pycr1_stromal_n['wilcoxon_p'], 4)}",
        f"- `PYCR1_Stromal_density`: n_pairs={int(pycr1_stromal_density['n_pairs'])}, mean_diff={format_value(pycr1_stromal_density['mean_diff'])}, median_diff={format_value(pycr1_stromal_density['median_diff'])}, p={format_value(pycr1_stromal_density['wilcoxon_p'], 4)}",
        f"- `PYCR1_Stromal_to_tumor`: n_pairs={int(pycr1_stromal_to_tumor['n_pairs'])}, mean_diff={format_value(pycr1_stromal_to_tumor['mean_diff'])}, median_diff={format_value(pycr1_stromal_to_tumor['median_diff'])}, p={format_value(pycr1_stromal_to_tumor['wilcoxon_p'], 4)}",
        f"- `PYCR1_Stromal_dist_to_tumor`: n_pairs={int(pycr1_stromal_dist_to_tumor['n_pairs'])}, mean_diff={format_value(pycr1_stromal_dist_to_tumor['mean_diff'])}, median_diff={format_value(pycr1_stromal_dist_to_tumor['median_diff'])}, p={format_value(pycr1_stromal_dist_to_tumor['wilcoxon_p'], 4)}",
        f"- `PYCR1_Stromal_dist_to_cd8`: n_pairs={int(pycr1_stromal_dist_to_cd8['n_pairs'])}, mean_diff={format_value(pycr1_stromal_dist_to_cd8['mean_diff'])}, median_diff={format_value(pycr1_stromal_dist_to_cd8['median_diff'])}, p={format_value(pycr1_stromal_dist_to_cd8['wilcoxon_p'], 4)}",
        f"- `CD8_T_dist_to_PYCR1_Stromal`: n_pairs={int(cd8_dist_to_pycr1_stromal['n_pairs'])}, mean_diff={format_value(cd8_dist_to_pycr1_stromal['mean_diff'])}, median_diff={format_value(cd8_dist_to_pycr1_stromal['median_diff'])}, p={format_value(cd8_dist_to_pycr1_stromal['wilcoxon_p'], 4)}",
        "",
        "解释：如果这个小群比大类基质更先出现显著变化，就更说明问题可能不是“所有基质都在挡路”，而是某个更具体的活跃基质亚群在起作用。",
        "",
        "不建议讲：",
        "",
        "- 不建议说“已经证明基质挡住了 CD8”。",
        "- 不建议把 `CD8_T_dist_to_tumor` 当前结果表述为显著结论。",
        "",
        "## 下一步研究方向",
        "",
        "下一步最值得推进的不是重复现在这套大类基质分析，而是把基质拆细，寻找真正可能和 `CD8` 排斥有关的亚群。",
        "",
        "建议优先顺序：",
        "",
        "- 先检查原始数据里是否有 `PYCR1` 等更具体的基质相关 marker。",
        "- 在当前第三轮主线代码框架里，把 `PYCR1+` 或 `PYCR1+基质细胞` 作为新的候选亚群接入。",
        "- 对该亚群重复当前已经成熟的指标体系：数量、密度、相对肿瘤比例、到 Tumor 距离、与 CD8 的距离关系。",
        "",
        "通俗讲：现在已经比较确定的是“CD8 变少了”，下一步要找的是“到底是哪一小群基质细胞可能在挡路”。",
        "",
    ]
    REPORT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")


def print_summary(sig_df: pd.DataFrame, sens_df: pd.DataFrame, loo_df: pd.DataFrame) -> None:
    print("\n===== 第三轮显著性结果（全部卵巢转移灶） =====")
    print(sig_df.sort_values(["wilcoxon_p", "metric"]).head(20).to_string(index=False))
    print("\n===== CD8极值敏感性分析 =====")
    print(sens_df.to_string(index=False))
    print("\n===== CD8留一法最敏感结果（按 p 值排序） =====")
    print(loo_df.sort_values(["metric", "p_after_removal"]).groupby("metric").head(5).to_string(index=False))
    print("\n输出目录：")
    print(OUT_DIR)


def main() -> None:
    _, pair_df = build_tables()
    sig_df = build_significance(pair_df)
    sens_df, loo_df = build_cd8_sensitivity(pair_df)

    make_line_grid(pair_df, ["Macrophage_n", "M2_like_Macrophage_n", "CD8_T_n", "Stromal_n"], OUT_DIR / "01_数量折线图.png", "五类细胞：数量维度（全部卵巢转移灶）")
    make_line_grid(pair_df, ["Macrophage_density", "M2_like_Macrophage_density", "CD8_T_density", "Stromal_density"], OUT_DIR / "02_密度折线图.png", "五类细胞：密度维度（全部卵巢转移灶）")
    make_line_grid(pair_df, ["M2_like_Macrophage_to_tumor", "CD8_T_to_tumor", "Stromal_to_tumor"], OUT_DIR / "03_Tumor归一化折线图.png", "五类细胞：Tumor归一化关系（全部卵巢转移灶）")
    make_line_grid(pair_df, ["M2_like_Macrophage_dist_to_tumor", "CD8_T_dist_to_tumor", "Stromal_dist_to_tumor"], OUT_DIR / "04_Tumor距离折线图.png", "五类细胞：到Tumor距离（全部卵巢转移灶）")
    make_line_grid(pair_df, ["M2_like_Macrophage_dist_to_stromal", "CD8_T_dist_to_stromal"], OUT_DIR / "05_基质距离折线图.png", "五类细胞：到基质距离（全部卵巢转移灶）")
    make_line_grid(pair_df, ["window_m2_stromal_frac", "window_cd8_tumor_frac", "window_tumor_stromal_frac"], OUT_DIR / "06_局部窗口折线图.png", "五类细胞：局部窗口模式（全部卵巢转移灶）")
    make_line_grid(pair_df, ["Stromal_n", "Stromal_density", "Stromal_to_tumor", "CD8_T_dist_to_stromal"], OUT_DIR / "07_补充折线图.png", "五类细胞：Stromal与CD8补充指标（全部卵巢转移灶）")
    make_heatmap(
        sig_df,
        [
            "CD8_T_n",
            "CD8_T_density",
            "CD8_T_to_tumor",
            "CD8_T_dist_to_tumor",
            "Stromal_n",
            "Stromal_density",
            "Stromal_to_tumor",
            "Stromal_dist_to_tumor",
            "CD8_T_dist_to_stromal",
            "PYCR1_Stromal_n",
            "PYCR1_Stromal_density",
            "PYCR1_Stromal_to_tumor",
            "PYCR1_Stromal_dist_to_tumor",
            "PYCR1_Stromal_dist_to_cd8",
            "CD8_T_dist_to_PYCR1_Stromal",
        ],
        OUT_DIR / "08_显著性热图.png",
    )
    make_cd8_sensitivity_plot(pair_df, sens_df, OUT_DIR / "09_CD8极值敏感性分析.png")
    make_line_grid(
        pair_df,
        ["PYCR1_Stromal_n", "PYCR1_Stromal_density", "PYCR1_Stromal_to_tumor"],
        OUT_DIR / "11_PYCR1基质数量比例图.png",
        "PYCR1阳性基质亚群：数量与比例（全部卵巢转移灶）",
    )
    make_line_grid(
        pair_df,
        ["PYCR1_Stromal_dist_to_tumor", "PYCR1_Stromal_dist_to_cd8", "CD8_T_dist_to_PYCR1_Stromal"],
        OUT_DIR / "12_PYCR1基质距离图.png",
        "PYCR1阳性基质亚群：距离关系（全部卵巢转移灶）",
    )
    write_report_summary(sig_df)
    print_summary(sig_df, sens_df, loo_df)


if __name__ == "__main__":
    main()
