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
OUT_DIR = Path("/Users/jia/Desktop/学习 /毕业设计/实验/3轮/round3_bcell_caf_20um")

SAMPLE_TABLE = OUT_DIR / "sample_summary.tsv"
PAIR_TABLE = OUT_DIR / "pair_metrics.tsv"
SIG_TABLE = OUT_DIR / "significance_summary.tsv"
REPORT_SUMMARY = OUT_DIR / "10_B细胞_CAF_20um分析总结.md"
PHENO_SAMPLE_TABLE = OUT_DIR / "phenotype_context_sample_summary.tsv"
PHENO_WITHIN_SOURCE_TABLE = OUT_DIR / "phenotype_within_source_stats.tsv"
PHENO_PAIR_CONTRAST_TABLE = OUT_DIR / "phenotype_pair_contrast_stats.tsv"

GRID_SIZE = 6
NEAR_RADIUS = 20.0
RADIUS_SERIES = [20.0, 30.0, 50.0]

PRIMARY_COLOR = "#2B6CB0"
MET_COLOR = "#C53030"
ACCENT_COLOR = "#2F855A"
GRID_COLOR = "#D9D9D9"

PLOT_METRICS = [
    "B_cell_n",
    "M2_like_Macrophage_n",
    "CD8_T_n",
    "CAF_n",
    "PYCR1_CAF_n",
    "CLDN18_Tumor_n",
    "Non_CLDN18_Tumor_n",
    "B_cell_density",
    "M2_like_Macrophage_density",
    "CD8_T_density",
    "CAF_density",
    "PYCR1_CAF_density",
    "CLDN18_Tumor_density",
    "Non_CLDN18_Tumor_density",
    "B_cell_to_tumor",
    "M2_like_Macrophage_to_tumor",
    "CD8_T_to_tumor",
    "CAF_to_tumor",
    "PYCR1_CAF_to_tumor",
    "CLDN18_Tumor_frac_of_tumor",
    "Non_CLDN18_Tumor_frac_of_tumor",
    "B_cell_near_tumor_frac",
    "B_cell_tumor_neighbors_per_cell",
    "CD8_T_near_tumor_frac",
    "CD8_T_tumor_neighbors_per_cell",
    "CAF_near_tumor_frac",
    "CAF_tumor_neighbors_per_cell",
    "CD8_T_near_CAF_frac",
    "CD8_T_CAF_neighbors_per_cell",
    "M2_like_Macrophage_near_CAF_frac",
    "M2_like_Macrophage_CAF_neighbors_per_cell",
    "PYCR1_CAF_near_tumor_frac",
    "PYCR1_CAF_tumor_neighbors_per_cell",
    "PYCR1_CAF_near_cd8_frac",
    "PYCR1_CAF_cd8_neighbors_per_cell",
    "CD8_T_near_PYCR1_CAF_frac",
    "CD8_T_PYCR1_CAF_neighbors_per_cell",
    "PYCR1_CAF_near_CLDN18_Tumor_frac",
    "PYCR1_CAF_CLDN18_Tumor_neighbors_per_cell",
    "PYCR1_CAF_near_Non_CLDN18_Tumor_frac",
    "PYCR1_CAF_Non_CLDN18_Tumor_neighbors_per_cell",
    "CLDN18_Tumor_near_cd8_frac",
    "CLDN18_Tumor_cd8_neighbors_per_tumor",
    "Non_CLDN18_Tumor_near_cd8_frac",
    "Non_CLDN18_Tumor_cd8_neighbors_per_tumor",
    "CLDN18_Tumor_near_PYCR1_CAF_frac",
    "Non_CLDN18_Tumor_near_PYCR1_CAF_frac",
    "CD8_T_near_CLDN18_Tumor_frac",
    "CD8_T_near_Non_CLDN18_Tumor_frac",
    "window_cd8_tumor_frac",
    "window_tumor_caf_frac",
    "window_cd8_caf_frac",
]

LABELS = {
    "B_cell_n": "B细胞数量",
    "M2_like_Macrophage_n": "M2样巨噬细胞数量",
    "CD8_T_n": "CD8阳性T细胞数量",
    "CAF_n": "CAF数量",
    "PYCR1_CAF_n": "PYCR1阳性CAF数量",
    "CLDN18_Tumor_n": "CLDN18.2阳性肿瘤数量",
    "Non_CLDN18_Tumor_n": "CLDN18.2阴性肿瘤数量",
    "B_cell_density": "B细胞相对密度",
    "M2_like_Macrophage_density": "M2样巨噬细胞相对密度",
    "CD8_T_density": "CD8阳性T细胞相对密度",
    "CAF_density": "CAF相对密度",
    "PYCR1_CAF_density": "PYCR1阳性CAF相对密度",
    "CLDN18_Tumor_density": "CLDN18.2阳性肿瘤相对密度",
    "Non_CLDN18_Tumor_density": "CLDN18.2阴性肿瘤相对密度",
    "B_cell_to_tumor": "B细胞 / 肿瘤",
    "M2_like_Macrophage_to_tumor": "M2样巨噬细胞 / 肿瘤",
    "CD8_T_to_tumor": "CD8阳性T细胞 / 肿瘤",
    "CAF_to_tumor": "CAF / 肿瘤",
    "PYCR1_CAF_to_tumor": "PYCR1阳性CAF / 肿瘤",
    "CLDN18_Tumor_frac_of_tumor": "CLDN18.2阳性肿瘤占全部肿瘤比例",
    "Non_CLDN18_Tumor_frac_of_tumor": "CLDN18.2阴性肿瘤占全部肿瘤比例",
    "B_cell_near_tumor_frac": "B细胞近Tumor比例(20μm)",
    "B_cell_tumor_neighbors_per_cell": "每个B细胞20μm内Tumor平均数",
    "CD8_T_near_tumor_frac": "CD8近Tumor比例(20μm)",
    "CD8_T_tumor_neighbors_per_cell": "每个CD8细胞20μm内Tumor平均数",
    "CAF_near_tumor_frac": "CAF近Tumor比例(20μm)",
    "CAF_tumor_neighbors_per_cell": "每个CAF细胞20μm内Tumor平均数",
    "CD8_T_near_CAF_frac": "CD8近CAF比例(20μm)",
    "CD8_T_CAF_neighbors_per_cell": "每个CD8细胞20μm内CAF平均数",
    "M2_like_Macrophage_near_CAF_frac": "M2样巨噬细胞近CAF比例(20μm)",
    "M2_like_Macrophage_CAF_neighbors_per_cell": "每个M2细胞20μm内CAF平均数",
    "PYCR1_CAF_near_tumor_frac": "PYCR1阳性CAF近Tumor比例(20μm)",
    "PYCR1_CAF_tumor_neighbors_per_cell": "每个PYCR1阳性CAF 20μm内Tumor平均数",
    "PYCR1_CAF_near_cd8_frac": "PYCR1阳性CAF近CD8比例(20μm)",
    "PYCR1_CAF_cd8_neighbors_per_cell": "每个PYCR1阳性CAF 20μm内CD8平均数",
    "CD8_T_near_PYCR1_CAF_frac": "CD8近PYCR1阳性CAF比例(20μm)",
    "CD8_T_PYCR1_CAF_neighbors_per_cell": "每个CD8细胞20μm内PYCR1阳性CAF平均数",
    "PYCR1_CAF_near_CLDN18_Tumor_frac": "PYCR1阳性CAF近CLDN18.2阳性肿瘤比例(20μm)",
    "PYCR1_CAF_CLDN18_Tumor_neighbors_per_cell": "每个PYCR1阳性CAF 20μm内CLDN18.2阳性肿瘤平均数",
    "PYCR1_CAF_near_Non_CLDN18_Tumor_frac": "PYCR1阳性CAF近CLDN18.2阴性肿瘤比例(20μm)",
    "PYCR1_CAF_Non_CLDN18_Tumor_neighbors_per_cell": "每个PYCR1阳性CAF 20μm内CLDN18.2阴性肿瘤平均数",
    "CLDN18_Tumor_near_cd8_frac": "CLDN18.2阳性肿瘤近CD8比例(20μm)",
    "CLDN18_Tumor_cd8_neighbors_per_tumor": "每个CLDN18.2阳性肿瘤20μm内CD8平均数",
    "Non_CLDN18_Tumor_near_cd8_frac": "CLDN18.2阴性肿瘤近CD8比例(20μm)",
    "Non_CLDN18_Tumor_cd8_neighbors_per_tumor": "每个CLDN18.2阴性肿瘤20μm内CD8平均数",
    "CLDN18_Tumor_near_PYCR1_CAF_frac": "CLDN18.2阳性肿瘤近PYCR1阳性CAF比例(20μm)",
    "Non_CLDN18_Tumor_near_PYCR1_CAF_frac": "CLDN18.2阴性肿瘤近PYCR1阳性CAF比例(20μm)",
    "CD8_T_near_CLDN18_Tumor_frac": "CD8近CLDN18.2阳性肿瘤比例(20μm)",
    "CD8_T_near_Non_CLDN18_Tumor_frac": "CD8近CLDN18.2阴性肿瘤比例(20μm)",
    "window_cd8_tumor_frac": "CD8+肿瘤共富集窗口占比",
    "window_tumor_caf_frac": "肿瘤+CAF共富集窗口占比",
    "window_cd8_caf_frac": "CD8+CAF共富集窗口占比",
}

TUMOR_PHENOTYPES = [
    ("CLDN18_Tumor", "is_cldn18_tumor", "CLDN18.2阳性肿瘤"),
    ("Non_CLDN18_Tumor", "is_non_cldn18_tumor", "CLDN18.2阴性肿瘤"),
]

CONTEXT_TARGETS = [
    ("CD8_T", "is_cd8_t", "CD8阳性T细胞"),
    ("B_cell", "is_b_cell", "B细胞"),
    ("M2_like_Macrophage", "is_m2_like_macrophage", "M2样巨噬细胞"),
    ("CAF", "is_caf", "CAF"),
    ("PYCR1_CAF", "is_pycr1_caf", "PYCR1阳性CAF"),
]


for radius in RADIUS_SERIES:
    r_text = f"{int(radius)}μm"
    for tumor_key, _, tumor_label in TUMOR_PHENOTYPES:
        for target_key, _, target_label in CONTEXT_TARGETS:
            LABELS[f"{tumor_key}_near_{target_key}_frac_r{int(radius)}"] = f"{tumor_label}近{target_label}比例({r_text})"
            LABELS[f"{tumor_key}_{target_key}_neighbors_per_tumor_r{int(radius)}"] = f"每个{tumor_label}{r_text}内{target_label}平均数"
            PLOT_METRICS.append(f"{tumor_key}_near_{target_key}_frac_r{int(radius)}")
            PLOT_METRICS.append(f"{tumor_key}_{target_key}_neighbors_per_tumor_r{int(radius)}")


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
        "cd20": pick_col(columns, aliases=["cd20"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd20"]),
        "cd68": pick_col(columns, aliases=["cd68"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd68"]),
        "cd163": pick_col(columns, aliases=["cd163"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd163"]),
        "cd3e": pick_col(columns, aliases=["cd3e"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd3e"]),
        "cd8": pick_col(columns, aliases=["cd8"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd8"]),
        "sma": pick_col(columns, aliases=["sma"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["sma"]),
        "vimentin": pick_col(columns, aliases=["vimentin"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["vimentin"]),
        "cd31": pick_col(columns, aliases=["cd31"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cd31"]),
        "pycr1": pick_col(columns, aliases=["pycr1"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["pycr1"]),
        "cldn18": pick_col(columns, aliases=["cldn18"], prefer_contains=["positivity"]) or pick_col(columns, aliases=["cldn18"]),
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


def sample_area(coords: np.ndarray) -> float:
    if len(coords) == 0:
        return np.nan
    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)
    return max(max_x - min_x, 1.0) * max(max_y - min_y, 1.0)


def get_coords(df: pd.DataFrame, flag_col: str) -> np.ndarray:
    sub = df[df[flag_col] == 1]
    return sub[["Center X", "Center Y"]].to_numpy(dtype=float) if len(sub) else np.empty((0, 2), dtype=float)


def fraction_within_radius(src_coords: np.ndarray, tgt_coords: np.ndarray, radius: float = NEAR_RADIUS) -> float:
    if len(src_coords) == 0 or len(tgt_coords) == 0:
        return np.nan
    tree = cKDTree(tgt_coords)
    src_coords = np.asarray(src_coords, dtype=float)
    try:
        counts = np.asarray(tree.query_ball_point(src_coords, r=radius, return_length=True), dtype=float)
    except TypeError:
        counts = np.array([len(tree.query_ball_point(point, r=radius)) for point in src_coords], dtype=float)
    if len(counts) == 0:
        return np.nan
    return float((counts > 0).mean())


def mean_neighbors_within_radius(src_coords: np.ndarray, tgt_coords: np.ndarray, radius: float = NEAR_RADIUS) -> float:
    if len(src_coords) == 0 or len(tgt_coords) == 0:
        return np.nan
    tree = cKDTree(tgt_coords)
    src_coords = np.asarray(src_coords, dtype=float)
    try:
        counts = np.asarray(tree.query_ball_point(src_coords, r=radius, return_length=True), dtype=float)
    except TypeError:
        counts = np.array([len(tree.query_ball_point(point, r=radius)) for point in src_coords], dtype=float)
    if len(counts) == 0:
        return np.nan
    return float(counts.mean())


def compute_window_metrics(df: pd.DataFrame) -> dict[str, float]:
    coords = df[["Center X", "Center Y"]].to_numpy(dtype=float)
    if len(coords) == 0:
        return {"window_cd8_tumor_frac": np.nan, "window_tumor_caf_frac": np.nan, "window_cd8_caf_frac": np.nan}
    min_x, min_y = coords.min(axis=0)
    max_x, max_y = coords.max(axis=0)
    width = max(max_x - min_x, 1.0)
    height = max(max_y - min_y, 1.0)
    tmp = df.copy()
    tmp["row"] = np.minimum(((tmp["Center Y"] - min_y) / height * GRID_SIZE).astype(int), GRID_SIZE - 1)
    tmp["col"] = np.minimum(((tmp["Center X"] - min_x) / width * GRID_SIZE).astype(int), GRID_SIZE - 1)
    count_cols = ["is_tumor", "is_cd8_t", "is_caf"]
    grouped = tmp.groupby(["row", "col"])[count_cols].sum().reindex(
        pd.MultiIndex.from_product([range(GRID_SIZE), range(GRID_SIZE)], names=["row", "col"]),
        fill_value=0,
    ).reset_index()
    tumor = grouped["is_tumor"].to_numpy(dtype=float)
    cd8 = grouped["is_cd8_t"].to_numpy(dtype=float)
    caf = grouped["is_caf"].to_numpy(dtype=float)
    total = tumor + cd8 + caf
    with np.errstate(divide="ignore", invalid="ignore"):
        tumor_density = np.divide(tumor, total, out=np.full_like(tumor, np.nan), where=total > 0)
        cd8_density = np.divide(cd8, total, out=np.full_like(cd8, np.nan), where=total > 0)
        caf_density = np.divide(caf, total, out=np.full_like(caf, np.nan), where=total > 0)
    return {
        "window_cd8_tumor_frac": float(((cd8_density >= 0.15) & (tumor_density >= 0.2)).mean()),
        "window_tumor_caf_frac": float(((tumor_density >= 0.2) & (caf_density >= 0.2)).mean()),
        "window_cd8_caf_frac": float(((cd8_density >= 0.15) & (caf_density >= 0.2)).mean()),
    }


def load_sample_from_raw(objects_file: Path) -> pd.DataFrame:
    header_df = pd.read_csv(objects_file, sep="\t", nrows=0)
    col_map = detect_required_columns(list(header_df.columns))
    usecols = [col_map[key] for key in ["x", "y", "panck", "cd20", "cd68", "cd163", "cd3e", "cd8", "sma", "vimentin", "cd31", "pycr1", "cldn18"]]
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
            "CD20": to_binary(raw_df[col_map["cd20"]]),
            "CD68": to_binary(raw_df[col_map["cd68"]]),
            "CD163": to_binary(raw_df[col_map["cd163"]]),
            "CD3e": to_binary(raw_df[col_map["cd3e"]]),
            "CD8": to_binary(raw_df[col_map["cd8"]]),
            "SMA": to_binary(raw_df[col_map["sma"]]),
            "Vimentin": to_binary(raw_df[col_map["vimentin"]]),
            "CD31": to_binary(raw_df[col_map["cd31"]]),
            "PYCR1": to_binary(raw_df[col_map["pycr1"]]),
            "CLDN18": to_binary(raw_df[col_map["cldn18"]]),
        }
    )
    df = df.dropna(subset=["Center X", "Center Y"]).copy()
    df["is_tumor"] = (df["PanCK"] == 1).astype(np.int8)
    df["is_b_cell"] = ((df["CD20"] == 1) & (df["PanCK"] == 0)).astype(np.int8)
    df["is_m2_like_macrophage"] = ((df["CD68"] == 1) & (df["CD163"] == 1) & (df["PanCK"] == 0)).astype(np.int8)
    df["is_cd8_t"] = ((df["CD3e"] == 1) & (df["CD8"] == 1) & (df["PanCK"] == 0)).astype(np.int8)
    df["is_caf"] = (((df["SMA"] == 1) | (df["Vimentin"] == 1)) & (df["CD31"] == 0) & (df["PanCK"] == 0)).astype(np.int8)
    df["is_pycr1_caf"] = ((df["PYCR1"] == 1) & (df["is_caf"] == 1)).astype(np.int8)
    df["is_cldn18_tumor"] = ((df["PanCK"] == 1) & (df["CLDN18"] == 1)).astype(np.int8)
    df["is_non_cldn18_tumor"] = ((df["PanCK"] == 1) & (df["CLDN18"] == 0)).astype(np.int8)
    return df


def compute_sample_metrics(df: pd.DataFrame) -> dict[str, float]:
    coords = df[["Center X", "Center Y"]].to_numpy(dtype=float)
    area = sample_area(coords)
    tumor_coords = get_coords(df, "is_tumor")
    caf_coords = get_coords(df, "is_caf")
    cd8_coords = get_coords(df, "is_cd8_t")
    pycr1_caf_coords = get_coords(df, "is_pycr1_caf")
    cldn18_tumor_coords = get_coords(df, "is_cldn18_tumor")
    non_cldn18_tumor_coords = get_coords(df, "is_non_cldn18_tumor")

    metrics = {"bbox_area": area}
    for key, flag_col in [
        ("Tumor", "is_tumor"),
        ("B_cell", "is_b_cell"),
        ("M2_like_Macrophage", "is_m2_like_macrophage"),
        ("CD8_T", "is_cd8_t"),
        ("CAF", "is_caf"),
        ("PYCR1_CAF", "is_pycr1_caf"),
        ("CLDN18_Tumor", "is_cldn18_tumor"),
        ("Non_CLDN18_Tumor", "is_non_cldn18_tumor"),
    ]:
        cell_coords = get_coords(df, flag_col)
        n = len(cell_coords)
        metrics[f"{key}_n"] = n
        metrics[f"{key}_density"] = safe_div(n * 1_000_000, area)
        if key != "Tumor":
            metrics[f"{key}_to_tumor"] = safe_div(n, len(tumor_coords))
            metrics[f"{key}_near_tumor_frac"] = fraction_within_radius(cell_coords, tumor_coords)
            metrics[f"{key}_tumor_neighbors_per_cell"] = mean_neighbors_within_radius(cell_coords, tumor_coords)
        if key in {"CD8_T", "M2_like_Macrophage"}:
            metrics[f"{key}_near_CAF_frac"] = fraction_within_radius(cell_coords, caf_coords)
            metrics[f"{key}_CAF_neighbors_per_cell"] = mean_neighbors_within_radius(cell_coords, caf_coords)
        if key == "PYCR1_CAF":
            metrics[f"{key}_near_cd8_frac"] = fraction_within_radius(cell_coords, cd8_coords)
            metrics[f"{key}_cd8_neighbors_per_cell"] = mean_neighbors_within_radius(cell_coords, cd8_coords)
            metrics[f"{key}_near_CLDN18_Tumor_frac"] = fraction_within_radius(cell_coords, cldn18_tumor_coords)
            metrics[f"{key}_CLDN18_Tumor_neighbors_per_cell"] = mean_neighbors_within_radius(cell_coords, cldn18_tumor_coords)
            metrics[f"{key}_near_Non_CLDN18_Tumor_frac"] = fraction_within_radius(cell_coords, non_cldn18_tumor_coords)
            metrics[f"{key}_Non_CLDN18_Tumor_neighbors_per_cell"] = mean_neighbors_within_radius(cell_coords, non_cldn18_tumor_coords)
        if key in {"CLDN18_Tumor", "Non_CLDN18_Tumor"}:
            metrics[f"{key}_frac_of_tumor"] = safe_div(n, len(tumor_coords))
            metrics[f"{key}_near_cd8_frac"] = fraction_within_radius(cell_coords, cd8_coords)
            metrics[f"{key}_cd8_neighbors_per_tumor"] = mean_neighbors_within_radius(cell_coords, cd8_coords)
            metrics[f"{key}_near_PYCR1_CAF_frac"] = fraction_within_radius(cell_coords, pycr1_caf_coords)
    metrics["CD8_T_near_PYCR1_CAF_frac"] = fraction_within_radius(cd8_coords, pycr1_caf_coords)
    metrics["CD8_T_PYCR1_CAF_neighbors_per_cell"] = mean_neighbors_within_radius(cd8_coords, pycr1_caf_coords)
    metrics["CD8_T_near_CLDN18_Tumor_frac"] = fraction_within_radius(cd8_coords, cldn18_tumor_coords)
    metrics["CD8_T_near_Non_CLDN18_Tumor_frac"] = fraction_within_radius(cd8_coords, non_cldn18_tumor_coords)

    target_coords_map = {
        "CD8_T": cd8_coords,
        "B_cell": get_coords(df, "is_b_cell"),
        "M2_like_Macrophage": get_coords(df, "is_m2_like_macrophage"),
        "CAF": caf_coords,
        "PYCR1_CAF": pycr1_caf_coords,
    }
    for tumor_key, tumor_flag, _ in TUMOR_PHENOTYPES:
        tumor_pheno_coords = get_coords(df, tumor_flag)
        for target_key, _, _ in CONTEXT_TARGETS:
            target_coords = target_coords_map[target_key]
            for radius in RADIUS_SERIES:
                r_int = int(radius)
                metrics[f"{tumor_key}_near_{target_key}_frac_r{r_int}"] = fraction_within_radius(
                    tumor_pheno_coords, target_coords, radius=radius
                )
                metrics[f"{tumor_key}_{target_key}_neighbors_per_tumor_r{r_int}"] = mean_neighbors_within_radius(
                    tumor_pheno_coords, target_coords, radius=radius
                )
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


def build_phenotype_context_tables(sample_df: pd.DataFrame, pair_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    sample_rows = []
    for _, row in sample_df.iterrows():
        source_group = "Ovarian_Met" if int(row["is_ovarian_met"]) == 1 else "Primary"
        for radius in RADIUS_SERIES:
            r_int = int(radius)
            for target_key, _, target_label in CONTEXT_TARGETS:
                pos_metric = f"CLDN18_Tumor_near_{target_key}_frac_r{r_int}"
                neg_metric = f"Non_CLDN18_Tumor_near_{target_key}_frac_r{r_int}"
                pos_neighbors = f"CLDN18_Tumor_{target_key}_neighbors_per_tumor_r{r_int}"
                neg_neighbors = f"Non_CLDN18_Tumor_{target_key}_neighbors_per_tumor_r{r_int}"
                sample_rows.append(
                    {
                        "patient_id": row["patient_id"],
                        "sample_name": row["sample_name"],
                        "sample_suffix": row["sample_suffix"],
                        "source_group": source_group,
                        "radius_um": r_int,
                        "target_key": target_key,
                        "target_label": target_label,
                        "positive_near_frac": row.get(pos_metric, np.nan),
                        "negative_near_frac": row.get(neg_metric, np.nan),
                        "diff_positive_minus_negative_near_frac": (
                            row.get(pos_metric, np.nan) - row.get(neg_metric, np.nan)
                            if pd.notna(row.get(pos_metric, np.nan)) and pd.notna(row.get(neg_metric, np.nan))
                            else np.nan
                        ),
                        "positive_neighbors_per_tumor": row.get(pos_neighbors, np.nan),
                        "negative_neighbors_per_tumor": row.get(neg_neighbors, np.nan),
                        "diff_positive_minus_negative_neighbors_per_tumor": (
                            row.get(pos_neighbors, np.nan) - row.get(neg_neighbors, np.nan)
                            if pd.notna(row.get(pos_neighbors, np.nan)) and pd.notna(row.get(neg_neighbors, np.nan))
                            else np.nan
                        ),
                    }
                )
    pheno_sample_df = pd.DataFrame(sample_rows).sort_values(
        ["source_group", "radius_um", "target_key", "patient_id", "sample_name"]
    ).reset_index(drop=True)
    round_numeric(pheno_sample_df).to_csv(PHENO_SAMPLE_TABLE, sep="\t", index=False)

    within_rows = []
    for source_group in ["Primary", "Ovarian_Met"]:
        sub = pheno_sample_df[pheno_sample_df["source_group"] == source_group]
        for radius in sorted(pheno_sample_df["radius_um"].unique()):
            sub_radius = sub[sub["radius_um"] == radius]
            for target_key, _, target_label in CONTEXT_TARGETS:
                sub_target = sub_radius[sub_radius["target_key"] == target_key]
                for value_col in [
                    "diff_positive_minus_negative_near_frac",
                    "diff_positive_minus_negative_neighbors_per_tumor",
                ]:
                    vals = sub_target[value_col].dropna()
                    p, n = paired_p(sub_target[value_col])
                    within_rows.append(
                        {
                            "source_group": source_group,
                            "radius_um": radius,
                            "target_key": target_key,
                            "target_label": target_label,
                            "comparison": "CLDN18阳性 - CLDN18阴性",
                            "value_type": value_col,
                            "n_samples": n,
                            "mean_positive": float(sub_target[value_col.replace('diff_positive_minus_negative_', 'positive_')].dropna().mean())
                            if value_col.replace("diff_positive_minus_negative_", "positive_") in sub_target.columns else np.nan,
                            "mean_negative": float(sub_target[value_col.replace('diff_positive_minus_negative_', 'negative_')].dropna().mean())
                            if value_col.replace("diff_positive_minus_negative_", "negative_") in sub_target.columns else np.nan,
                            "mean_diff": float(vals.mean()) if len(vals) else np.nan,
                            "median_diff": float(vals.median()) if len(vals) else np.nan,
                            "wilcoxon_p": p,
                        }
                    )
    within_df = round_numeric(pd.DataFrame(within_rows))
    within_df.to_csv(PHENO_WITHIN_SOURCE_TABLE, sep="\t", index=False)

    pair_rows = []
    for radius in RADIUS_SERIES:
        r_int = int(radius)
        for target_key, _, target_label in CONTEXT_TARGETS:
            for value_suffix in ["near_frac", "neighbors_per_tumor"]:
                pos_metric = f"CLDN18_Tumor_{'near_' + target_key + '_frac' if value_suffix == 'near_frac' else target_key + '_neighbors_per_tumor'}_r{r_int}"
                neg_metric = f"Non_CLDN18_Tumor_{'near_' + target_key + '_frac' if value_suffix == 'near_frac' else target_key + '_neighbors_per_tumor'}_r{r_int}"
                diff_col = f"contrast_{target_key}_{value_suffix}_r{r_int}"
                tmp = pair_df.copy()
                tmp[diff_col] = np.nan
                valid = tmp[[f"primary_{pos_metric}", f"primary_{neg_metric}", f"met_{pos_metric}", f"met_{neg_metric}"]].notna().all(axis=1)
                tmp.loc[valid, diff_col] = (
                    (tmp.loc[valid, f"met_{pos_metric}"] - tmp.loc[valid, f"met_{neg_metric}"])
                    - (tmp.loc[valid, f"primary_{pos_metric}"] - tmp.loc[valid, f"primary_{neg_metric}"])
                )
                vals = tmp[diff_col].dropna()
                p, n = paired_p(tmp[diff_col])
                pair_rows.append(
                    {
                        "radius_um": r_int,
                        "target_key": target_key,
                        "target_label": target_label,
                        "value_type": value_suffix,
                        "comparison": "(转移灶内阳性-阴性) - (原发灶内阳性-阴性)",
                        "n_pairs": n,
                        "mean_diff": float(vals.mean()) if len(vals) else np.nan,
                        "median_diff": float(vals.median()) if len(vals) else np.nan,
                        "wilcoxon_p": p,
                    }
                )
    contrast_df = round_numeric(pd.DataFrame(pair_rows))
    contrast_df.to_csv(PHENO_PAIR_CONTRAST_TABLE, sep="\t", index=False)
    return pheno_sample_df, within_df, contrast_df


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
    fig, axes = plt.subplots(len(metrics), 1, figsize=(6.4, 3.6 * len(metrics)))
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
    fig, ax = plt.subplots(figsize=(5.8, max(4.2, 0.48 * len(metrics))))
    im = ax.imshow(vals, cmap="YlGnBu_r", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks([0], ["P值"])
    ax.set_yticks(np.arange(len(metrics)), [LABELS.get(m, m) for m in metrics])
    ax.set_title("B细胞 / CAF / 20μm邻域显著性热图", fontsize=14)
    for r in range(len(metrics)):
        v = vals[r, 0]
        ax.text(0, r, format_value(v, 4) if pd.notna(v) else "NA", ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def make_source_compare_heatmap(within_df: pd.DataFrame, targets: list[str], value_type: str, out_path: Path, title: str) -> None:
    subset = within_df[(within_df["target_key"].isin(targets)) & (within_df["value_type"] == value_type)].copy()
    sources = ["Primary", "Ovarian_Met"]
    radii = [int(r) for r in RADIUS_SERIES]
    cols = [f"{source}_{radius}um" for source in sources for radius in radii]
    heat = pd.DataFrame(index=targets, columns=cols, dtype=float)
    for target in targets:
        for source in sources:
            for radius in radii:
                row = subset[
                    (subset["target_key"] == target)
                    & (subset["source_group"] == source)
                    & (subset["radius_um"] == radius)
                ]
                if not row.empty:
                    heat.loc[target, f"{source}_{radius}um"] = row.iloc[0]["wilcoxon_p"]
    vals = heat.to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8.2, max(3.8, 0.8 * len(targets))))
    im = ax.imshow(vals, cmap="YlOrRd_r", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(np.arange(len(cols)), cols, rotation=30, ha="right")
    ax.set_yticks(np.arange(len(targets)), [LABELS.get(f"CLDN18_Tumor_near_{t}_frac_r20", t) if value_type == "diff_positive_minus_negative_near_frac" else LABELS.get(f"CLDN18_Tumor_{t}_neighbors_per_tumor_r20", t) for t in targets])
    ax.set_title(title, fontsize=13)
    for r in range(vals.shape[0]):
        for c in range(vals.shape[1]):
            v = vals[r, c]
            ax.text(c, r, format_value(v, 4) if pd.notna(v) else "NA", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def get_sig_row(sig_df: pd.DataFrame, metric: str) -> pd.Series:
    row = sig_df[sig_df["metric"] == metric]
    if row.empty:
        raise KeyError(f"未找到指标：{metric}")
    return row.iloc[0]


def get_within_row(within_df: pd.DataFrame, source_group: str, radius_um: int, target_key: str, value_type: str) -> pd.Series:
    row = within_df[
        (within_df["source_group"] == source_group)
        & (within_df["radius_um"] == radius_um)
        & (within_df["target_key"] == target_key)
        & (within_df["value_type"] == value_type)
    ]
    if row.empty:
        raise KeyError(f"未找到分层指标：{source_group}, {radius_um}, {target_key}, {value_type}")
    return row.iloc[0]


def get_contrast_row(contrast_df: pd.DataFrame, radius_um: int, target_key: str, value_type: str) -> pd.Series:
    row = contrast_df[
        (contrast_df["radius_um"] == radius_um)
        & (contrast_df["target_key"] == target_key)
        & (contrast_df["value_type"] == value_type)
    ]
    if row.empty:
        raise KeyError(f"未找到对比指标：{radius_um}, {target_key}, {value_type}")
    return row.iloc[0]


def write_report_summary(sig_df: pd.DataFrame, within_df: pd.DataFrame, contrast_df: pd.DataFrame) -> None:
    metrics = {
        k: get_sig_row(sig_df, k)
        for k in [
            "CD8_T_n",
            "CD8_T_density",
            "CD8_T_to_tumor",
            "CD8_T_near_tumor_frac",
            "CD8_T_tumor_neighbors_per_cell",
            "B_cell_n",
            "B_cell_density",
            "B_cell_to_tumor",
            "CAF_n",
            "CAF_density",
            "CAF_to_tumor",
            "CAF_near_tumor_frac",
            "CD8_T_near_CAF_frac",
            "PYCR1_CAF_near_tumor_frac",
            "PYCR1_CAF_near_cd8_frac",
            "Non_CLDN18_Tumor_frac_of_tumor",
            "CLDN18_Tumor_cd8_neighbors_per_tumor",
            "Non_CLDN18_Tumor_cd8_neighbors_per_tumor",
            "CLDN18_Tumor_near_cd8_frac",
            "Non_CLDN18_Tumor_near_cd8_frac",
            "CLDN18_Tumor_near_PYCR1_CAF_frac",
            "Non_CLDN18_Tumor_near_PYCR1_CAF_frac",
            "PYCR1_CAF_near_CLDN18_Tumor_frac",
            "PYCR1_CAF_near_Non_CLDN18_Tumor_frac",
        ]
    }
    extra = {
        "primary_cd8_20_frac": get_within_row(within_df, "Primary", 20, "CD8_T", "diff_positive_minus_negative_near_frac"),
        "met_cd8_20_frac": get_within_row(within_df, "Ovarian_Met", 20, "CD8_T", "diff_positive_minus_negative_near_frac"),
        "primary_cd8_30_frac": get_within_row(within_df, "Primary", 30, "CD8_T", "diff_positive_minus_negative_near_frac"),
        "met_cd8_30_frac": get_within_row(within_df, "Ovarian_Met", 30, "CD8_T", "diff_positive_minus_negative_near_frac"),
        "primary_cd8_50_frac": get_within_row(within_df, "Primary", 50, "CD8_T", "diff_positive_minus_negative_near_frac"),
        "met_cd8_50_frac": get_within_row(within_df, "Ovarian_Met", 50, "CD8_T", "diff_positive_minus_negative_near_frac"),
        "primary_b_20_frac": get_within_row(within_df, "Primary", 20, "B_cell", "diff_positive_minus_negative_near_frac"),
        "met_b_20_frac": get_within_row(within_df, "Ovarian_Met", 20, "B_cell", "diff_positive_minus_negative_near_frac"),
        "primary_m2_20_frac": get_within_row(within_df, "Primary", 20, "M2_like_Macrophage", "diff_positive_minus_negative_near_frac"),
        "met_m2_20_frac": get_within_row(within_df, "Ovarian_Met", 20, "M2_like_Macrophage", "diff_positive_minus_negative_near_frac"),
        "primary_caf_20_frac": get_within_row(within_df, "Primary", 20, "CAF", "diff_positive_minus_negative_near_frac"),
        "met_caf_20_frac": get_within_row(within_df, "Ovarian_Met", 20, "CAF", "diff_positive_minus_negative_near_frac"),
        "primary_pycr1_20_frac": get_within_row(within_df, "Primary", 20, "PYCR1_CAF", "diff_positive_minus_negative_near_frac"),
        "met_pycr1_20_frac": get_within_row(within_df, "Ovarian_Met", 20, "PYCR1_CAF", "diff_positive_minus_negative_near_frac"),
        "cd8_20_contrast": get_contrast_row(contrast_df, 20, "CD8_T", "near_frac"),
        "cd8_30_contrast": get_contrast_row(contrast_df, 30, "CD8_T", "near_frac"),
        "cd8_50_contrast": get_contrast_row(contrast_df, 50, "CD8_T", "near_frac"),
    }
    lines = [
        "# B细胞 + CAF + 20μm邻域分析总结",
        "",
        "## 本轮代码改动",
        "",
        "- 删除了总巨噬细胞（Macrophage）大类，替换为 `B细胞 = CD20+ & PanCK-`。",
        "- 将 `Stromal` 全部重命名为 `CAF`，定义为 `(Vimentin+ 或 α-SMA+) & CD31- & PanCK-`。",
        "- 空间邻近统一改成以细胞为圆心、20μm邻域内的 `近邻比例` 和 `平均邻居数`。",
        "",
        "## 当前最稳的主线",
        "",
        f"- `CD8_T_n`: mean_diff={format_value(metrics['CD8_T_n']['mean_diff'])}, median_diff={format_value(metrics['CD8_T_n']['median_diff'])}, p={format_value(metrics['CD8_T_n']['wilcoxon_p'], 4)}",
        f"- `CD8_T_density`: mean_diff={format_value(metrics['CD8_T_density']['mean_diff'])}, median_diff={format_value(metrics['CD8_T_density']['median_diff'])}, p={format_value(metrics['CD8_T_density']['wilcoxon_p'], 4)}",
        f"- `CD8_T_to_tumor`: mean_diff={format_value(metrics['CD8_T_to_tumor']['mean_diff'])}, median_diff={format_value(metrics['CD8_T_to_tumor']['median_diff'])}, p={format_value(metrics['CD8_T_to_tumor']['wilcoxon_p'], 4)}",
        "",
        "解释：无论改不改空间邻近方法，`CD8+T` 下降仍然应该是最先看的主结论。",
        "",
        "## 20μm邻域下，CD8 与肿瘤的关系",
        "",
        f"- `CD8_T_near_tumor_frac`: mean_diff={format_value(metrics['CD8_T_near_tumor_frac']['mean_diff'])}, median_diff={format_value(metrics['CD8_T_near_tumor_frac']['median_diff'])}, p={format_value(metrics['CD8_T_near_tumor_frac']['wilcoxon_p'], 4)}",
        f"- `CD8_T_tumor_neighbors_per_cell`: mean_diff={format_value(metrics['CD8_T_tumor_neighbors_per_cell']['mean_diff'])}, median_diff={format_value(metrics['CD8_T_tumor_neighbors_per_cell']['median_diff'])}, p={format_value(metrics['CD8_T_tumor_neighbors_per_cell']['wilcoxon_p'], 4)}",
        "",
        "解释：这里不再讲“离得远不远”，只讲20μm小邻域里，CD8 身边还有没有肿瘤、平均能碰到多少肿瘤。",
        "",
        "## B细胞结果",
        "",
        f"- `B_cell_n`: mean_diff={format_value(metrics['B_cell_n']['mean_diff'])}, median_diff={format_value(metrics['B_cell_n']['median_diff'])}, p={format_value(metrics['B_cell_n']['wilcoxon_p'], 4)}",
        f"- `B_cell_density`: mean_diff={format_value(metrics['B_cell_density']['mean_diff'])}, median_diff={format_value(metrics['B_cell_density']['median_diff'])}, p={format_value(metrics['B_cell_density']['wilcoxon_p'], 4)}",
        f"- `B_cell_to_tumor`: mean_diff={format_value(metrics['B_cell_to_tumor']['mean_diff'])}, median_diff={format_value(metrics['B_cell_to_tumor']['median_diff'])}, p={format_value(metrics['B_cell_to_tumor']['wilcoxon_p'], 4)}",
        "",
        "解释：这部分用来代替原来的总巨噬细胞大类，观察转移灶里 B 细胞是否出现更清楚的变化。",
        "",
        "## CAF 与 CD8 / 肿瘤的关系",
        "",
        f"- `CAF_n`: mean_diff={format_value(metrics['CAF_n']['mean_diff'])}, median_diff={format_value(metrics['CAF_n']['median_diff'])}, p={format_value(metrics['CAF_n']['wilcoxon_p'], 4)}",
        f"- `CAF_density`: mean_diff={format_value(metrics['CAF_density']['mean_diff'])}, median_diff={format_value(metrics['CAF_density']['median_diff'])}, p={format_value(metrics['CAF_density']['wilcoxon_p'], 4)}",
        f"- `CAF_to_tumor`: mean_diff={format_value(metrics['CAF_to_tumor']['mean_diff'])}, median_diff={format_value(metrics['CAF_to_tumor']['median_diff'])}, p={format_value(metrics['CAF_to_tumor']['wilcoxon_p'], 4)}",
        f"- `CAF_near_tumor_frac`: mean_diff={format_value(metrics['CAF_near_tumor_frac']['mean_diff'])}, median_diff={format_value(metrics['CAF_near_tumor_frac']['median_diff'])}, p={format_value(metrics['CAF_near_tumor_frac']['wilcoxon_p'], 4)}",
        f"- `CD8_T_near_CAF_frac`: mean_diff={format_value(metrics['CD8_T_near_CAF_frac']['mean_diff'])}, median_diff={format_value(metrics['CD8_T_near_CAF_frac']['median_diff'])}, p={format_value(metrics['CD8_T_near_CAF_frac']['wilcoxon_p'], 4)}",
        "",
        "解释：这里看的是20μm小邻域里，CAF和肿瘤有没有更常同处一圈，CD8又是不是更常贴着CAF。",
        "",
        "## PYCR1阳性CAF 与 CLDN18.2肿瘤",
        "",
        f"- `PYCR1_CAF_near_tumor_frac`: mean_diff={format_value(metrics['PYCR1_CAF_near_tumor_frac']['mean_diff'])}, median_diff={format_value(metrics['PYCR1_CAF_near_tumor_frac']['median_diff'])}, p={format_value(metrics['PYCR1_CAF_near_tumor_frac']['wilcoxon_p'], 4)}",
        f"- `PYCR1_CAF_near_cd8_frac`: mean_diff={format_value(metrics['PYCR1_CAF_near_cd8_frac']['mean_diff'])}, median_diff={format_value(metrics['PYCR1_CAF_near_cd8_frac']['median_diff'])}, p={format_value(metrics['PYCR1_CAF_near_cd8_frac']['wilcoxon_p'], 4)}",
        f"- `PYCR1_CAF_near_CLDN18_Tumor_frac`: mean_diff={format_value(metrics['PYCR1_CAF_near_CLDN18_Tumor_frac']['mean_diff'])}, median_diff={format_value(metrics['PYCR1_CAF_near_CLDN18_Tumor_frac']['median_diff'])}, p={format_value(metrics['PYCR1_CAF_near_CLDN18_Tumor_frac']['wilcoxon_p'], 4)}",
        f"- `PYCR1_CAF_near_Non_CLDN18_Tumor_frac`: mean_diff={format_value(metrics['PYCR1_CAF_near_Non_CLDN18_Tumor_frac']['mean_diff'])}, median_diff={format_value(metrics['PYCR1_CAF_near_Non_CLDN18_Tumor_frac']['median_diff'])}, p={format_value(metrics['PYCR1_CAF_near_Non_CLDN18_Tumor_frac']['wilcoxon_p'], 4)}",
        f"- `Non_CLDN18_Tumor_frac_of_tumor`: mean_diff={format_value(metrics['Non_CLDN18_Tumor_frac_of_tumor']['mean_diff'])}, median_diff={format_value(metrics['Non_CLDN18_Tumor_frac_of_tumor']['median_diff'])}, p={format_value(metrics['Non_CLDN18_Tumor_frac_of_tumor']['wilcoxon_p'], 4)}",
        f"- `CLDN18_Tumor_cd8_neighbors_per_tumor`: mean_diff={format_value(metrics['CLDN18_Tumor_cd8_neighbors_per_tumor']['mean_diff'])}, median_diff={format_value(metrics['CLDN18_Tumor_cd8_neighbors_per_tumor']['median_diff'])}, p={format_value(metrics['CLDN18_Tumor_cd8_neighbors_per_tumor']['wilcoxon_p'], 4)}",
        f"- `Non_CLDN18_Tumor_cd8_neighbors_per_tumor`: mean_diff={format_value(metrics['Non_CLDN18_Tumor_cd8_neighbors_per_tumor']['mean_diff'])}, median_diff={format_value(metrics['Non_CLDN18_Tumor_cd8_neighbors_per_tumor']['median_diff'])}, p={format_value(metrics['Non_CLDN18_Tumor_cd8_neighbors_per_tumor']['wilcoxon_p'], 4)}",
        f"- `CLDN18_Tumor_near_cd8_frac`: mean_diff={format_value(metrics['CLDN18_Tumor_near_cd8_frac']['mean_diff'])}, median_diff={format_value(metrics['CLDN18_Tumor_near_cd8_frac']['median_diff'])}, p={format_value(metrics['CLDN18_Tumor_near_cd8_frac']['wilcoxon_p'], 4)}",
        f"- `Non_CLDN18_Tumor_near_cd8_frac`: mean_diff={format_value(metrics['Non_CLDN18_Tumor_near_cd8_frac']['mean_diff'])}, median_diff={format_value(metrics['Non_CLDN18_Tumor_near_cd8_frac']['median_diff'])}, p={format_value(metrics['Non_CLDN18_Tumor_near_cd8_frac']['wilcoxon_p'], 4)}",
        f"- `CLDN18_Tumor_near_PYCR1_CAF_frac`: mean_diff={format_value(metrics['CLDN18_Tumor_near_PYCR1_CAF_frac']['mean_diff'])}, median_diff={format_value(metrics['CLDN18_Tumor_near_PYCR1_CAF_frac']['median_diff'])}, p={format_value(metrics['CLDN18_Tumor_near_PYCR1_CAF_frac']['wilcoxon_p'], 4)}",
        f"- `Non_CLDN18_Tumor_near_PYCR1_CAF_frac`: mean_diff={format_value(metrics['Non_CLDN18_Tumor_near_PYCR1_CAF_frac']['mean_diff'])}, median_diff={format_value(metrics['Non_CLDN18_Tumor_near_PYCR1_CAF_frac']['median_diff'])}, p={format_value(metrics['Non_CLDN18_Tumor_near_PYCR1_CAF_frac']['wilcoxon_p'], 4)}",
        "",
        "解释：这一段现在把 CLDN18.2阳性和阴性肿瘤完全拆开看，不再混成一个总 Tumor。重点看的是20μm局部小圈里，它们和 CD8、和 PYCR1+CAF 的接触是不是一起变少。",
        "",
        "## 新增：阳性肿瘤 vs 阴性肿瘤的多半径空间验证",
        "",
        "这里的 diff 定义为 `CLDN18.2阳性 - CLDN18.2阴性`。",
        "如果 diff < 0，表示阳性肿瘤周围这种细胞更少。",
        "",
        "### 1. 阳性肿瘤周围的 CD8 是否持续更少",
        "",
        f"- 原发灶 20μm：mean_diff={format_value(extra['primary_cd8_20_frac']['mean_diff'])}, p={format_value(extra['primary_cd8_20_frac']['wilcoxon_p'], 4)}",
        f"- 转移灶 20μm：mean_diff={format_value(extra['met_cd8_20_frac']['mean_diff'])}, p={format_value(extra['met_cd8_20_frac']['wilcoxon_p'], 4)}",
        f"- 原发灶 30μm：mean_diff={format_value(extra['primary_cd8_30_frac']['mean_diff'])}, p={format_value(extra['primary_cd8_30_frac']['wilcoxon_p'], 4)}",
        f"- 转移灶 30μm：mean_diff={format_value(extra['met_cd8_30_frac']['mean_diff'])}, p={format_value(extra['met_cd8_30_frac']['wilcoxon_p'], 4)}",
        f"- 原发灶 50μm：mean_diff={format_value(extra['primary_cd8_50_frac']['mean_diff'])}, p={format_value(extra['primary_cd8_50_frac']['wilcoxon_p'], 4)}",
        f"- 转移灶 50μm：mean_diff={format_value(extra['met_cd8_50_frac']['mean_diff'])}, p={format_value(extra['met_cd8_50_frac']['wilcoxon_p'], 4)}",
        f"- 转移灶相对原发灶是否更明显 20μm：mean_diff={format_value(extra['cd8_20_contrast']['mean_diff'])}, p={format_value(extra['cd8_20_contrast']['wilcoxon_p'], 4)}",
        f"- 转移灶相对原发灶是否更明显 30μm：mean_diff={format_value(extra['cd8_30_contrast']['mean_diff'])}, p={format_value(extra['cd8_30_contrast']['wilcoxon_p'], 4)}",
        f"- 转移灶相对原发灶是否更明显 50μm：mean_diff={format_value(extra['cd8_50_contrast']['mean_diff'])}, p={format_value(extra['cd8_50_contrast']['wilcoxon_p'], 4)}",
        "",
        "### 2. 阳性肿瘤周围减少的只是 CD8，还是别的细胞也一起少",
        "",
        f"- B细胞 原发20μm：mean_diff={format_value(extra['primary_b_20_frac']['mean_diff'])}, p={format_value(extra['primary_b_20_frac']['wilcoxon_p'], 4)}",
        f"- B细胞 转移20μm：mean_diff={format_value(extra['met_b_20_frac']['mean_diff'])}, p={format_value(extra['met_b_20_frac']['wilcoxon_p'], 4)}",
        f"- M2样巨噬细胞 原发20μm：mean_diff={format_value(extra['primary_m2_20_frac']['mean_diff'])}, p={format_value(extra['primary_m2_20_frac']['wilcoxon_p'], 4)}",
        f"- M2样巨噬细胞 转移20μm：mean_diff={format_value(extra['met_m2_20_frac']['mean_diff'])}, p={format_value(extra['met_m2_20_frac']['wilcoxon_p'], 4)}",
        "",
        "### 3. 阳性肿瘤周围 CAF / PYCR1+CAF 是否更富集",
        "",
        f"- CAF 原发20μm：mean_diff={format_value(extra['primary_caf_20_frac']['mean_diff'])}, p={format_value(extra['primary_caf_20_frac']['wilcoxon_p'], 4)}",
        f"- CAF 转移20μm：mean_diff={format_value(extra['met_caf_20_frac']['mean_diff'])}, p={format_value(extra['met_caf_20_frac']['wilcoxon_p'], 4)}",
        f"- PYCR1+CAF 原发20μm：mean_diff={format_value(extra['primary_pycr1_20_frac']['mean_diff'])}, p={format_value(extra['primary_pycr1_20_frac']['wilcoxon_p'], 4)}",
        f"- PYCR1+CAF 转移20μm：mean_diff={format_value(extra['met_pycr1_20_frac']['mean_diff'])}, p={format_value(extra['met_pycr1_20_frac']['wilcoxon_p'], 4)}",
        "",
        "解释：如果阳性肿瘤周围 CD8 更少，同时 CAF / PYCR1+CAF 更高，就更接近“肿瘤表型变化 + 基质生态位解组 + 局部免疫减弱”这条解释链；如果只看到 CD8 变少而 CAF 不变，就更像单纯的局部免疫冷化。",
        "",
    ]
    REPORT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")


def print_summary(sig_df: pd.DataFrame, within_df: pd.DataFrame, contrast_df: pd.DataFrame) -> None:
    print("\n===== B细胞 / CAF / 20μm邻域显著性结果 =====")
    print(sig_df.sort_values(["wilcoxon_p", "metric"]).head(30).to_string(index=False))
    print("\n===== 阳性肿瘤 vs 阴性肿瘤：原发/转移内部分层结果（近邻比例） =====")
    print(
        within_df[within_df["value_type"] == "diff_positive_minus_negative_near_frac"]
        .sort_values(["wilcoxon_p", "source_group", "radius_um", "target_key"])
        .head(30)
        .to_string(index=False)
    )
    print("\n===== 阳性-阴性差值：转移灶是否比原发灶更明显 =====")
    print(contrast_df.sort_values(["wilcoxon_p", "radius_um", "target_key"]).head(20).to_string(index=False))
    print("\n输出目录：")
    print(OUT_DIR)


def main() -> None:
    sample_df, pair_df = build_tables()
    sig_df = build_significance(pair_df)
    _, within_df, contrast_df = build_phenotype_context_tables(sample_df, pair_df)

    make_line_grid(pair_df, ["B_cell_n", "M2_like_Macrophage_n", "CD8_T_n", "CAF_n"], OUT_DIR / "01_数量折线图.png", "B细胞 / M2 / CD8 / CAF：数量维度")
    make_line_grid(pair_df, ["B_cell_density", "M2_like_Macrophage_density", "CD8_T_density", "CAF_density"], OUT_DIR / "02_密度折线图.png", "B细胞 / M2 / CD8 / CAF：密度维度")
    make_line_grid(pair_df, ["B_cell_to_tumor", "M2_like_Macrophage_to_tumor", "CD8_T_to_tumor", "CAF_to_tumor"], OUT_DIR / "03_Tumor归一化折线图.png", "B细胞 / M2 / CD8 / CAF：Tumor归一化关系")
    make_line_grid(pair_df, ["B_cell_near_tumor_frac", "CD8_T_near_tumor_frac", "CAF_near_tumor_frac"], OUT_DIR / "04_近Tumor比例折线图.png", "20μm邻域：近Tumor比例")
    make_line_grid(pair_df, ["B_cell_tumor_neighbors_per_cell", "CD8_T_tumor_neighbors_per_cell", "CAF_tumor_neighbors_per_cell"], OUT_DIR / "05_Tumor邻居数折线图.png", "20μm邻域：Tumor邻居平均数")
    make_line_grid(pair_df, ["CD8_T_near_CAF_frac", "CD8_T_PYCR1_CAF_neighbors_per_cell", "PYCR1_CAF_near_cd8_frac", "PYCR1_CAF_cd8_neighbors_per_cell"], OUT_DIR / "06_CAF与CD8折线图.png", "CAF / PYCR1+CAF 与 CD8")
    make_line_grid(pair_df, ["CLDN18_Tumor_frac_of_tumor", "Non_CLDN18_Tumor_frac_of_tumor"], OUT_DIR / "07_CLDN18表型占比折线图.png", "肿瘤表型占比：CLDN18.2阳性 vs 阴性")
    make_line_grid(pair_df, ["CLDN18_Tumor_near_cd8_frac", "Non_CLDN18_Tumor_near_cd8_frac", "CLDN18_Tumor_cd8_neighbors_per_tumor", "Non_CLDN18_Tumor_cd8_neighbors_per_tumor"], OUT_DIR / "08_CLDN18与CD8折线图.png", "阳性/阴性肿瘤分别与 CD8 比较")
    make_line_grid(pair_df, ["PYCR1_CAF_near_CLDN18_Tumor_frac", "PYCR1_CAF_near_Non_CLDN18_Tumor_frac", "PYCR1_CAF_CLDN18_Tumor_neighbors_per_cell", "PYCR1_CAF_Non_CLDN18_Tumor_neighbors_per_cell"], OUT_DIR / "09_PYCR1_CAF与阳阴性肿瘤折线图.png", "PYCR1+CAF 与阳性/阴性肿瘤分别比较")
    make_line_grid(pair_df, ["CLDN18_Tumor_near_PYCR1_CAF_frac", "Non_CLDN18_Tumor_near_PYCR1_CAF_frac", "CD8_T_near_CLDN18_Tumor_frac", "CD8_T_near_Non_CLDN18_Tumor_frac"], OUT_DIR / "10_阳阴性肿瘤与PYCR1_CAF_CD8折线图.png", "阳性/阴性肿瘤与 PYCR1+CAF / CD8 分别比较")
    make_line_grid(pair_df, ["window_cd8_tumor_frac", "window_tumor_caf_frac", "window_cd8_caf_frac"], OUT_DIR / "11_局部窗口折线图.png", "局部窗口模式")
    make_heatmap(
        sig_df,
        [
            "CD8_T_n", "CD8_T_density", "CD8_T_to_tumor",
            "CD8_T_near_tumor_frac", "CD8_T_tumor_neighbors_per_cell",
            "B_cell_n", "B_cell_density", "B_cell_to_tumor", "B_cell_near_tumor_frac", "B_cell_tumor_neighbors_per_cell",
            "CAF_n", "CAF_density", "CAF_to_tumor", "CAF_near_tumor_frac", "CD8_T_near_CAF_frac",
            "PYCR1_CAF_near_tumor_frac", "PYCR1_CAF_near_cd8_frac", "PYCR1_CAF_cd8_neighbors_per_cell",
            "CLDN18_Tumor_frac_of_tumor", "Non_CLDN18_Tumor_frac_of_tumor",
            "CLDN18_Tumor_near_cd8_frac", "Non_CLDN18_Tumor_near_cd8_frac",
            "CLDN18_Tumor_cd8_neighbors_per_tumor", "Non_CLDN18_Tumor_cd8_neighbors_per_tumor",
            "CD8_T_near_CLDN18_Tumor_frac", "CD8_T_near_Non_CLDN18_Tumor_frac",
            "PYCR1_CAF_near_CLDN18_Tumor_frac", "PYCR1_CAF_near_Non_CLDN18_Tumor_frac",
            "PYCR1_CAF_CLDN18_Tumor_neighbors_per_cell", "PYCR1_CAF_Non_CLDN18_Tumor_neighbors_per_cell",
            "CLDN18_Tumor_near_PYCR1_CAF_frac", "Non_CLDN18_Tumor_near_PYCR1_CAF_frac",
        ],
        OUT_DIR / "12_显著性热图.png",
    )
    make_source_compare_heatmap(
        within_df,
        ["CD8_T", "B_cell", "M2_like_Macrophage"],
        "diff_positive_minus_negative_near_frac",
        OUT_DIR / "13_阳阴性肿瘤_免疫细胞近邻比例热图.png",
        "阳性肿瘤 vs 阴性肿瘤：免疫细胞近邻比例P值热图",
    )
    make_source_compare_heatmap(
        within_df,
        ["CAF", "PYCR1_CAF"],
        "diff_positive_minus_negative_near_frac",
        OUT_DIR / "14_阳阴性肿瘤_CAF_PYCR1近邻比例热图.png",
        "阳性肿瘤 vs 阴性肿瘤：CAF / PYCR1+CAF近邻比例P值热图",
    )
    write_report_summary(sig_df, within_df, contrast_df)
    print_summary(sig_df, within_df, contrast_df)


if __name__ == "__main__":
    main()
