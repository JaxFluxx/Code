# -*- coding: utf-8 -*-
"""
CODEX raw objects.tsv -> clean sample tables
Mac version

输出：
/Users/jia/Desktop/学习 /毕业设计/实验/CODEX_clean_baseline/
  ├── sample_summary.tsv
  ├── pair_manifest.tsv
  └── samples/
      ├── 1P/
      │   ├── 1P_clean_all.tsv
      │   └── 1P_analysis_cells.tsv
      ├── 1L/
      │   ├── 1L_clean_all.tsv
      │   └── 1L_analysis_cells.tsv
      └── ...

说明：
- 自动在每个样本文件夹里寻找“文件名包含 objects 且体积最大的文件”
- 自动识别坐标列与 marker positivity 列
- baseline 细胞定义：
    Tumor = PanCK+ & CD68-
    Mac    = CD68+ & PanCK-
    M1     = CD68+ & CD86+  & CD163- & PanCK-
    M2     = CD68+ & CD163+ & CD86-  & PanCK-
    ambiguous_mac = CD68+ & CD86+ & CD163+ & PanCK-
"""

from pathlib import Path
import pandas as pd
import numpy as np
import shutil
import re

# =========================
# 0) PATHS
# =========================
EXPERIMENT_ROOT = Path("/Users/jia/Desktop/学习 /毕业设计/实验")
RAW_ROOT = EXPERIMENT_ROOT / "CODEX全部分析数据-20260116"
OUT_DIR = EXPERIMENT_ROOT / "CODEX_clean_baseline"
SAMPLES_OUT_DIR = OUT_DIR / "samples"

# overwrite
if OUT_DIR.exists():
    shutil.rmtree(OUT_DIR)
SAMPLES_OUT_DIR.mkdir(parents=True, exist_ok=True)

if not RAW_ROOT.exists():
    raise FileNotFoundError(f"找不到原始数据目录：{RAW_ROOT}")

# =========================
# 1) HELPERS
# =========================
def norm_text(x: str) -> str:
    """列名标准化：小写 + 去掉非字母数字"""
    return re.sub(r"[^a-z0-9]+", "", str(x).lower())

def find_largest_objects_file(sample_dir: Path):
    candidates = [
        p for p in sample_dir.iterdir()
        if p.is_file() and "objects" in p.name.lower()
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_size)

def pick_col(columns, aliases, prefer_contains=None):
    """
    在 columns 中找最合适的列
    aliases: 必须匹配到的关键词之一（标准化后）
    prefer_contains: 若提供，优先包含这些关键词
    """
    norm_map = {c: norm_text(c) for c in columns}
    candidates = [c for c in columns if any(a in norm_map[c] for a in aliases)]
    if not candidates:
        return None

    if prefer_contains:
        preferred = [c for c in candidates if all(k in norm_map[c] for k in prefer_contains)]
        if preferred:
            candidates = preferred

    # 优先选列名更短者（通常更“标准”）
    candidates = sorted(candidates, key=lambda c: (len(norm_map[c]), len(str(c))))
    return candidates[0]

def detect_required_columns(df: pd.DataFrame):
    cols = list(df.columns)

    x_col = pick_col(
        cols,
        aliases=["centerx", "centroidx", "xcenter", "positionx", "locationx", "xcoord", "coordx"]
    )
    y_col = pick_col(
        cols,
        aliases=["centery", "centroidy", "ycenter", "positiony", "locationy", "ycoord", "coordy"]
    )

    panck_col = pick_col(
        cols,
        aliases=["pancytokeratin", "panck", "pancytokeratin"],
        prefer_contains=["positivity"]
    ) or pick_col(
        cols,
        aliases=["pancytokeratin", "panck", "pancytokeratin"]
    )

    cd68_col = pick_col(cols, aliases=["cd68"], prefer_contains=["positivity"]) or pick_col(cols, aliases=["cd68"])
    cd86_col = pick_col(cols, aliases=["cd86"], prefer_contains=["positivity"]) or pick_col(cols, aliases=["cd86"])
    cd163_col = pick_col(cols, aliases=["cd163"], prefer_contains=["positivity"]) or pick_col(cols, aliases=["cd163"])

    # 可选 id 列
    id_col = pick_col(
        cols,
        aliases=["objectid", "cellid", "id", "objectnumber"]
    )

    required = {
        "cell_id": id_col,
        "x": x_col,
        "y": y_col,
        "panck": panck_col,
        "cd68": cd68_col,
        "cd86": cd86_col,
        "cd163": cd163_col,
    }

    missing = [k for k, v in required.items() if k != "cell_id" and v is None]
    if missing:
        raise ValueError(f"缺少关键列：{missing}\n实际列名示例：{list(df.columns)[:30]}")
    return required

def to_numeric_binary(series: pd.Series) -> pd.Series:
    """把 positivity 列安全转成 0/1"""
    x = pd.to_numeric(series, errors="coerce").fillna(0)
    return (x > 0.5).astype(np.int8)

def parse_sample_name(sample_name: str):
    """
    解析样本名，如：
    1P / 1L / 5R / 13QT
    返回: (patient_id, suffix)
    """
    m = re.match(r"^(\d+)(P|L|R|QT)$", str(sample_name).strip(), flags=re.IGNORECASE)
    if not m:
        return None, None
    return int(m.group(1)), m.group(2).upper()

def cell_type_from_flags(row):
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

# =========================
# 2) SCAN SAMPLE DIRS
# =========================
sample_dirs = [p for p in RAW_ROOT.iterdir() if p.is_dir()]
sample_dirs = sorted(sample_dirs, key=lambda p: p.name)

sample_summary_rows = []
pair_index = {}  # {patient_id: {"P": sample, "L": sample, "R": sample, "QT": sample}}

print(f"共发现样本文件夹：{len(sample_dirs)}")

for sample_dir in sample_dirs:
    sample_name = sample_dir.name.strip()
    patient_id, suffix = parse_sample_name(sample_name)

    # 只处理命名规范的样本文件夹
    if patient_id is None:
        print(f"[跳过] 非标准样本文件夹：{sample_dir.name}")
        continue

    objects_file = find_largest_objects_file(sample_dir)
    if objects_file is None:
        print(f"[跳过] {sample_name} 文件夹内未找到包含 objects 的文件")
        continue

    print(f"[读取] {sample_name} <- {objects_file.name}")

    try:
        df = pd.read_csv(objects_file, sep="\t", low_memory=False)
    except Exception as e:
        print(f"[失败] {sample_name} 读取出错：{e}")
        continue

    try:
        colmap = detect_required_columns(df)
    except Exception as e:
        print(f"[失败] {sample_name} 列识别出错：{e}")
        continue

    # 构建 clean_all
    if colmap["cell_id"] is not None:
        cell_id = df[colmap["cell_id"]]
    else:
        cell_id = pd.Series(np.arange(len(df)), index=df.index, name="cell_id_auto")

    clean = pd.DataFrame({
        "cell_id": cell_id,
        "Center X": pd.to_numeric(df[colmap["x"]], errors="coerce"),
        "Center Y": pd.to_numeric(df[colmap["y"]], errors="coerce"),
        "PanCK": to_numeric_binary(df[colmap["panck"]]),
        "CD68": to_numeric_binary(df[colmap["cd68"]]),
        "CD86": to_numeric_binary(df[colmap["cd86"]]),
        "CD163": to_numeric_binary(df[colmap["cd163"]]),
    })

    clean["sample_name"] = sample_name
    clean["patient_id"] = patient_id
    clean["sample_suffix"] = suffix
    clean["source_file"] = str(objects_file)

    # 去掉无坐标
    clean = clean.dropna(subset=["Center X", "Center Y"]).copy()

    # baseline flags
    clean["is_tumor"] = ((clean["PanCK"] == 1) & (clean["CD68"] == 0)).astype(np.int8)
    clean["is_mac"] = ((clean["CD68"] == 1) & (clean["PanCK"] == 0)).astype(np.int8)
    clean["is_m1"] = ((clean["CD68"] == 1) & (clean["CD86"] == 1) & (clean["CD163"] == 0) & (clean["PanCK"] == 0)).astype(np.int8)
    clean["is_m2"] = ((clean["CD68"] == 1) & (clean["CD163"] == 1) & (clean["CD86"] == 0) & (clean["PanCK"] == 0)).astype(np.int8)
    clean["is_ambiguous_mac"] = ((clean["CD68"] == 1) & (clean["CD86"] == 1) & (clean["CD163"] == 1) & (clean["PanCK"] == 0)).astype(np.int8)

    clean["cell_type"] = clean.apply(cell_type_from_flags, axis=1)

    # 只保留后续分析需要的 Tumor / M1 / M2
    analysis_cells = clean[clean["cell_type"].isin(["Tumor", "M1", "M2"])].copy()

    # 输出
    sample_out_dir = SAMPLES_OUT_DIR / sample_name
    sample_out_dir.mkdir(parents=True, exist_ok=True)

    clean_all_path = sample_out_dir / f"{sample_name}_clean_all.tsv"
    analysis_path = sample_out_dir / f"{sample_name}_analysis_cells.tsv"

    clean.to_csv(clean_all_path, sep="\t", index=False)
    analysis_cells.to_csv(analysis_path, sep="\t", index=False)

    # summary
    tumor_n = int((analysis_cells["cell_type"] == "Tumor").sum())
    m1_n = int((analysis_cells["cell_type"] == "M1").sum())
    m2_n = int((analysis_cells["cell_type"] == "M2").sum())
    mac_n = m1_n + m2_n
    m2_frac = (m2_n / mac_n) if mac_n > 0 else np.nan

    sample_summary_rows.append({
        "patient_id": patient_id,
        "sample_name": sample_name,
        "sample_suffix": suffix,
        "source_file": str(objects_file),
        "n_total_clean_rows": int(len(clean)),
        "tumor_n": tumor_n,
        "m1_n": m1_n,
        "m2_n": m2_n,
        "m2_frac_of_mac": m2_frac,
        "clean_all_path": str(clean_all_path),
        "analysis_cells_path": str(analysis_path),
    })

    if patient_id not in pair_index:
        pair_index[patient_id] = {}
    pair_index[patient_id][suffix] = {
        "sample_name": sample_name,
        "clean_all_path": str(clean_all_path),
        "analysis_cells_path": str(analysis_path),
    }

# =========================
# 3) SAVE SAMPLE SUMMARY
# =========================
sample_summary_df = pd.DataFrame(sample_summary_rows).sort_values(
    ["patient_id", "sample_suffix", "sample_name"]
).reset_index(drop=True)

sample_summary_path = OUT_DIR / "sample_summary.tsv"
sample_summary_df.to_csv(sample_summary_path, sep="\t", index=False)

# =========================
# 4) BUILD PAIR MANIFEST
# =========================
pair_rows = []

for patient_id in sorted(pair_index.keys()):
    info = pair_index[patient_id]
    if "P" not in info:
        continue

    primary = info["P"]
    for met_suffix in ["L", "R", "QT"]:
        if met_suffix not in info:
            continue
        met = info[met_suffix]

        pair_rows.append({
            "patient_id": patient_id,
            "primary_sample": primary["sample_name"],
            "met_sample": met["sample_name"],
            "met_suffix": met_suffix,
            "primary_clean_all_path": primary["clean_all_path"],
            "primary_analysis_path": primary["analysis_cells_path"],
            "met_clean_all_path": met["clean_all_path"],
            "met_analysis_path": met["analysis_cells_path"],
        })

pair_manifest_df = pd.DataFrame(pair_rows).sort_values(
    ["patient_id", "met_suffix", "primary_sample", "met_sample"]
).reset_index(drop=True)

pair_manifest_path = OUT_DIR / "pair_manifest.tsv"
pair_manifest_df.to_csv(pair_manifest_path, sep="\t", index=False)

print("\n✅ 预处理完成")
print(f"- clean输出目录：{OUT_DIR}")
print(f"- 样本汇总表：{sample_summary_path}")
print(f"- 配对清单：{pair_manifest_path}")
print(f"- 共生成样本 clean 表：{len(sample_summary_df)} 个")
print(f"- 共生成样本对：{len(pair_manifest_df)} 对")