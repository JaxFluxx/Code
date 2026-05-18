#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a self-contained CODEX paired-sample spatial evidence website.

The output is intentionally static: index.html + data.js.  This lets the site
open directly in a browser or through `python -m http.server` without needing a
backend during thesis defense.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Dict, Iterable

import numpy as np
import pandas as pd


OUT = Path("/Users/jia/Desktop/学习 /毕业设计/结项答辩！/论文/test-2/5_CODEX配对样本空间证据展示系统")
ROOT = Path("/Users/jia/Desktop/学习 /毕业设计/实验")
RAW_ROOT = ROOT / "CODEX全部分析数据-20260116"
CD8_SAMPLE = ROOT / "3轮/round3_cd8_pure_immune/sample_summary.tsv"
CD8_PAIR = ROOT / "3轮/round3_cd8_pure_immune/pair_metrics.tsv"
BCELL_SAMPLE = ROOT / "3轮/round3_bcell_caf_20um/sample_summary.tsv"
BCELL_PAIR = ROOT / "3轮/round3_bcell_caf_20um/pair_metrics.tsv"

RNG = np.random.default_rng(20260508)


CELL_TYPES = [
    "Tumor",
    "CD8_T",
    "B_cell",
    "CAF",
    "PYCR1_CAF",
    "CLDN18_Tumor",
    "Non_CLDN18_Tumor",
]


def object_path(sample: str) -> Path:
    matches = sorted((RAW_ROOT / sample).glob("*objects.tsv"))
    if not matches:
        matches = sorted((RAW_ROOT / sample).glob("*objects*.tsv"))
    if not matches:
        raise FileNotFoundError(f"No objects file for {sample}")
    return matches[0]


def find_marker_col(cols: Iterable[str], marker: str) -> str | None:
    marker = marker.lower().replace(" ", "")
    candidates = []
    for c in cols:
        cl = c.lower().replace(" ", "")
        if not cl.startswith("positivity-"):
            continue
        token = re.sub(r"^positivity-", "", cl)
        token = re.sub(r"\(.*?\)", "", token)
        token = token.replace("-", "").replace("_", "")
        target = marker.replace("-", "").replace("_", "")
        # Some exports prefix marker names with UUIDs, e.g.
        # `Positivity - <uuid>-CD8 (MX)`.  Match terminal tokens as well as
        # plain marker names.
        if token == target or token.startswith(target) or token.endswith(target):
            candidates.append(c)
    return candidates[0] if candidates else None


def read_classified(sample: str) -> pd.DataFrame:
    p = object_path(sample)
    head = pd.read_csv(p, sep="\t", nrows=0)
    cols = list(head.columns)
    needed = ["Center X", "Center Y"]
    markers = {
        "PanCK": "Pan-Cytokeratin",
        "CD8": "CD8",
        "CD3e": "CD3e",
        "CD20": "CD20",
        "Vimentin": "Vimentin",
        "SMA": "SMA",
        "CD31": "CD31",
        "PYCR1": "PYCR1",
        "CLDN18": "DAB CLDN18.2",
    }
    marker_cols = {k: find_marker_col(cols, v) for k, v in markers.items()}
    if marker_cols.get("CLDN18") is None:
        marker_cols["CLDN18"] = find_marker_col(cols, "DAB")
    for c in marker_cols.values():
        if c and c not in needed:
            needed.append(c)
    df = pd.read_csv(p, sep="\t", usecols=needed)
    df = df.rename(columns={"Center X": "x", "Center Y": "y"})
    df["x"] = pd.to_numeric(df["x"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df = df.dropna(subset=["x", "y"]).copy()

    def pos(name: str) -> pd.Series:
        col = marker_cols.get(name)
        if not col or col not in df.columns:
            return pd.Series(False, index=df.index)
        return pd.to_numeric(df[col], errors="coerce").fillna(0).gt(0)

    panck = pos("PanCK")
    cd8 = pos("CD8")
    cd3e = pos("CD3e")
    cd20 = pos("CD20")
    vim = pos("Vimentin")
    sma = pos("SMA")
    cd31 = pos("CD31")
    pycr1 = pos("PYCR1")
    cldn = pos("CLDN18")
    tumor = panck
    caf = (vim | sma) & (~cd31) & (~panck)
    out = pd.DataFrame(
        {
            "x": df["x"].astype(float),
            "y": df["y"].astype(float),
            "Tumor": tumor.astype(bool),
            "CD8_T": (cd3e & cd8 & (~panck)).astype(bool),
            "B_cell": (cd20 & (~panck)).astype(bool),
            "CAF": caf.astype(bool),
            "PYCR1_CAF": (pycr1 & caf).astype(bool),
            "CLDN18_Tumor": (tumor & cldn).astype(bool),
            "Non_CLDN18_Tumor": (tumor & (~cldn)).astype(bool),
        }
    )
    return out


def balanced_points(df: pd.DataFrame, max_per_type: Dict[str, int] | None = None, common_frac: float | None = None) -> list[dict]:
    max_per_type = max_per_type or {
        "Tumor": 4200,
        "CD8_T": 4200,
        "B_cell": 2200,
        "CAF": 1800,
        "PYCR1_CAF": 1400,
        "CLDN18_Tumor": 2400,
        "Non_CLDN18_Tumor": 2400,
    }
    chosen = set()
    for ct in CELL_TYPES:
        idx = df.index[df[ct]].to_numpy()
        if len(idx) == 0:
            continue
        if common_frac is not None:
            n = min(len(idx), max(1, int(len(idx) * common_frac)), max_per_type.get(ct, 1200))
        else:
            n = min(len(idx), max_per_type.get(ct, 1200))
        pick = RNG.choice(idx, size=n, replace=False)
        chosen.update(map(int, pick))
    sub = df.loc[sorted(chosen)].copy()
    points = []
    for _, r in sub.iterrows():
        flags = [ct for ct in CELL_TYPES if bool(r[ct])]
        # Draw CLDN phenotypes as tumor subtypes instead of extra duplicate cells.
        if "CLDN18_Tumor" in flags:
            primary = "CLDN18_Tumor"
        elif "Non_CLDN18_Tumor" in flags:
            primary = "Non_CLDN18_Tumor"
        elif "CD8_T" in flags:
            primary = "CD8_T"
        elif "B_cell" in flags:
            primary = "B_cell"
        elif "PYCR1_CAF" in flags:
            primary = "PYCR1_CAF"
        elif "CAF" in flags:
            primary = "CAF"
        elif "Tumor" in flags:
            primary = "Tumor"
        else:
            continue
        points.append(
            {
                "x": round(float(r["x"]), 3),
                "y": round(float(r["y"]), 3),
                "type": primary,
                "flags": flags,
            }
        )
    return points


def bounds(df: pd.DataFrame) -> dict:
    return {
        "xmin": float(df["x"].min()),
        "xmax": float(df["x"].max()),
        "ymin": float(df["y"].min()),
        "ymax": float(df["y"].max()),
    }


def choose_roi(df: pd.DataFrame, purpose: str = "overview") -> dict:
    b = bounds(df)
    w = max((b["xmax"] - b["xmin"]) * 0.22, 1000)
    h = max((b["ymax"] - b["ymin"]) * 0.22, 1000)
    xs = np.linspace(b["xmin"], b["xmax"] - w, 8)
    ys = np.linspace(b["ymin"], b["ymax"] - h, 8)
    best = None
    for x0 in xs:
        for y0 in ys:
            sub = df[(df.x >= x0) & (df.x <= x0 + w) & (df.y >= y0) & (df.y <= y0 + h)]
            tumor_n = int(sub["Tumor"].sum())
            cd8_n = int(sub["CD8_T"].sum())
            b_n = int(sub["B_cell"].sum())
            py_n = int(sub["PYCR1_CAF"].sum())
            cldn_n = int(sub["CLDN18_Tumor"].sum())
            non_cldn_n = int(sub["Non_CLDN18_Tumor"].sum())
            # Different tour steps need different "evidence windows":
            # a CD8 step should zoom to CD8-rich/tumor-adjacent regions, whereas
            # a B-cell step should not reuse the same CD8 ROI.
            if purpose == "cd8":
                score = min(cd8_n / 60, 28) + min(tumor_n / 350, 14)
            elif purpose == "local_cd8":
                score = min(tumor_n / 300, 22) + min(cd8_n / 80, 12) + min(cldn_n / 250, 8)
            elif purpose == "bcell":
                score = min(b_n / 35, 28) + min(tumor_n / 450, 8)
            elif purpose == "cldn":
                score = min((cldn_n + non_cldn_n) / 350, 22) + min(abs(cldn_n - non_cldn_n) / 180, 10) + min(cd8_n / 120, 5)
            elif purpose == "pycr1":
                score = min(py_n / 45, 24) + min(cd8_n / 100, 9) + min(tumor_n / 500, 7)
            else:
                score = min(tumor_n / 300, 20) + min(cd8_n / 50, 20) + min((b_n + py_n) / 40, 8)
            if best is None or score > best[0]:
                best = (score, x0, x0 + w, y0, y0 + h)
    _, x0, x1, y0, y1 = best
    sub = df[(df.x >= x0) & (df.x <= x1) & (df.y >= y0) & (df.y <= y1)]
    tumor_xy = sub.loc[sub["Tumor"], ["x", "y"]].to_numpy(float)
    cd8_xy = sub.loc[sub["CD8_T"], ["x", "y"]].to_numpy(float)
    neighbor = 0.0
    if len(tumor_xy) and len(cd8_xy):
        # Chunked 20um neighbor count: enough for ROI summary, not for main stats.
        counts = []
        for start in range(0, len(tumor_xy), 800):
            block = tumor_xy[start : start + 800]
            d2 = ((block[:, None, :] - cd8_xy[None, :, :]) ** 2).sum(axis=2)
            counts.append((d2 <= 20 * 20).sum(axis=1))
        neighbor = float(np.concatenate(counts).mean())
    return {
        "x0": round(float(x0), 3),
        "x1": round(float(x1), 3),
        "y0": round(float(y0), 3),
        "y1": round(float(y1), 3),
        "metrics": {
            "Tumor": int(sub["Tumor"].sum()),
            "CD8_T": int(sub["CD8_T"].sum()),
            "B_cell": int(sub["B_cell"].sum()),
            "PYCR1_CAF": int(sub["PYCR1_CAF"].sum()),
            "CLDN18_Tumor": int(sub["CLDN18_Tumor"].sum()),
            "Non_CLDN18_Tumor": int(sub["Non_CLDN18_Tumor"].sum()),
            "tumor_cd8_neighbors20": round(neighbor, 3),
        },
        "purpose": purpose,
    }


def rel_change(primary: float, met: float) -> float | None:
    if primary is None or not np.isfinite(primary) or abs(primary) < 1e-12:
        return None
    return (met - primary) / primary * 100


def fmt_float(x: float | None, nd=3):
    if x is None or not np.isfinite(x):
        return None
    return round(float(x), nd)


def build_data() -> dict:
    cd8_sample = pd.read_csv(CD8_SAMPLE, sep="\t")
    cd8_pair = pd.read_csv(CD8_PAIR, sep="\t")
    bcell_sample = pd.read_csv(BCELL_SAMPLE, sep="\t")
    bcell_pair = pd.read_csv(BCELL_PAIR, sep="\t")

    # Keep the final ovarian-metastasis 12-pair analysis used in the thesis.
    pairs = cd8_pair[cd8_pair["met_sample"].astype(str).str.endswith("R") | cd8_pair["met_sample"].astype(str).str.endswith("L")].copy()
    pairs = pairs.sort_values("patient_id")

    samples_needed = sorted(set(pairs["primary_sample"].astype(str)) | set(pairs["met_sample"].astype(str)))
    sample_data = {}
    raw_cache = {}
    for sample in samples_needed:
        print(f"Preparing {sample} ...")
        df = read_classified(sample)
        raw_cache[sample] = df

    # Use a shared sampling fraction within each Primary/Metastasis pair. This
    # preserves visible abundance differences better than independent per-type
    # caps, which can make a depleted metastasis look artificially dense.
    sample_frac: Dict[str, float] = {}
    for _, row in pairs.iterrows():
        p, m = str(row["primary_sample"]), str(row["met_sample"])
        key_counts = []
        for s in [p, m]:
            df = raw_cache[s]
            key_counts.append(int((df[["Tumor", "CD8_T", "B_cell", "CAF", "PYCR1_CAF"]].any(axis=1)).sum()))
        frac = min(1.0, 22000 / max(key_counts))
        sample_frac[p] = frac
        sample_frac[m] = frac

    for sample in samples_needed:
        df = raw_cache[sample]
        sample_row = cd8_sample.loc[cd8_sample["sample_name"].astype(str) == sample]
        bcell_row = bcell_sample.loc[bcell_sample["sample_name"].astype(str) == sample]
        sample_data[sample] = {
            "sample": sample,
            "patient_id": int(sample_row["patient_id"].iloc[0]) if not sample_row.empty else int(re.sub(r"\D", "", sample) or 0),
            "sample_type": "Metastasis" if sample.endswith(("R", "L")) else "Primary",
            "total_cells": int(len(df)),
            "bounds": bounds(df),
            "roi": choose_roi(df),
            "rois": {
                "overview": choose_roi(df, "overview"),
                "cd8": choose_roi(df, "cd8"),
                "local_cd8": choose_roi(df, "local_cd8"),
                "bcell": choose_roi(df, "bcell"),
                "cldn": choose_roi(df, "cldn"),
                "pycr1": choose_roi(df, "pycr1"),
            },
            "points": balanced_points(df, common_frac=sample_frac.get(sample)),
            "metrics": {
                "CD8_T_n": fmt_float(sample_row["CD8_T_n"].iloc[0], 0) if not sample_row.empty else None,
                "CD8_T_density": fmt_float(sample_row["CD8_T_density"].iloc[0], 3) if not sample_row.empty else None,
                "CD8_T_to_tumor": fmt_float(sample_row["CD8_T_to_tumor"].iloc[0], 4) if not sample_row.empty else None,
                "tumor_cd8_neighbors": fmt_float(sample_row["CLDN18_Tumor_cd8_neighbors_per_tumor"].iloc[0], 3) if not sample_row.empty else None,
                "B_cell_n": fmt_float(bcell_row["B_cell_n"].iloc[0], 0) if not bcell_row.empty and "B_cell_n" in bcell_row else None,
                "B_cell_density": fmt_float(bcell_row["B_cell_density"].iloc[0], 3) if not bcell_row.empty and "B_cell_density" in bcell_row else None,
            },
        }

    pair_data = []
    for _, row in pairs.iterrows():
        p, m = str(row["primary_sample"]), str(row["met_sample"])
        bp = bcell_pair.loc[bcell_pair["pair_label"].astype(str) == row["pair_label"]]
        def from_pair(metric: str):
            return fmt_float(row.get(f"primary_{metric}")), fmt_float(row.get(f"met_{metric}"))
        cards = []
        card_defs = [
            ("CD8_T_n", "CD8+T 细胞数量", "个"),
            ("CD8_T_density", "CD8+T 细胞密度", "/面积"),
            ("CD8_T_to_tumor", "CD8_T/Tumor 比例", ""),
            ("CLDN18_Tumor_cd8_neighbors_per_tumor", "肿瘤周围 CD8 平均邻居数", "个/肿瘤"),
        ]
        for metric, label, unit in card_defs:
            pr = float(row.get(f"primary_{metric}", np.nan))
            mt = float(row.get(f"met_{metric}", np.nan))
            cards.append(
                {
                    "metric": metric,
                    "label": label,
                    "unit": unit,
                    "primary": fmt_float(pr),
                    "met": fmt_float(mt),
                    "diff": fmt_float(mt - pr),
                    "relative_change": fmt_float(rel_change(pr, mt), 1),
                    "direction": "down" if mt < pr else ("up" if mt > pr else "flat"),
                }
            )
        pair_data.append(
            {
                "patient_id": int(row["patient_id"]),
                "pair_label": str(row["pair_label"]),
                "primary_sample": p,
                "met_sample": m,
                "cards": cards,
                "metrics": {k: fmt_float(v) for k, v in row.items() if isinstance(k, str) and k.startswith(("primary_", "met_", "diff_")) and isinstance(v, (int, float, np.integer, np.floating))},
            }
        )

    stat_panels = [
        {
            "id": "CD8_T_density",
            "title": "CD8+T 密度",
            "target": ["CD8_T"],
            "rows": [
                {"pair": r["pair_label"], "primary": r["metrics"].get("primary_CD8_T_density"), "met": r["metrics"].get("met_CD8_T_density")}
                for r in pair_data
            ],
        },
        {
            "id": "B_cell_density",
            "title": "B 细胞密度",
            "target": ["B_cell"],
            "rows": [
                {
                    "pair": str(r["pair_label"]),
                    "primary": fmt_float(bcell_pair.loc[bcell_pair["pair_label"].astype(str) == r["pair_label"], "primary_B_cell_density"].iloc[0]) if len(bcell_pair.loc[bcell_pair["pair_label"].astype(str) == r["pair_label"]]) else None,
                    "met": fmt_float(bcell_pair.loc[bcell_pair["pair_label"].astype(str) == r["pair_label"], "met_B_cell_density"].iloc[0]) if len(bcell_pair.loc[bcell_pair["pair_label"].astype(str) == r["pair_label"]]) else None,
                }
                for r in pair_data
            ],
        },
        {
            "id": "CLDN18_Tumor_frac",
            "title": "CLDN18.2 阳/阴性肿瘤比例",
            "target": ["CLDN18_Tumor", "Non_CLDN18_Tumor"],
            "rows": [
                {"pair": r["pair_label"], "primary": r["metrics"].get("primary_CLDN18_Tumor_frac_of_tumor"), "met": r["metrics"].get("met_CLDN18_Tumor_frac_of_tumor")}
                for r in pair_data
            ],
        },
        {
            "id": "PYCR1_CAF_near_cd8_frac",
            "title": "PYCR1+CAF 与 CD8 局部联系",
            "target": ["PYCR1_CAF", "CD8_T"],
            "rows": [
                {
                    "pair": str(r["pair_label"]),
                    "primary": fmt_float(bcell_pair.loc[bcell_pair["pair_label"].astype(str) == r["pair_label"], "primary_PYCR1_CAF_near_cd8_frac"].iloc[0]) if len(bcell_pair.loc[bcell_pair["pair_label"].astype(str) == r["pair_label"]]) else None,
                    "met": fmt_float(bcell_pair.loc[bcell_pair["pair_label"].astype(str) == r["pair_label"], "met_PYCR1_CAF_near_cd8_frac"].iloc[0]) if len(bcell_pair.loc[bcell_pair["pair_label"].astype(str) == r["pair_label"]]) else None,
                }
                for r in pair_data
            ],
        },
    ]
    default_pair_index = 0
    if pair_data:
        default_pair_index = int(
            np.argmin([
                r["metrics"].get("diff_CD8_T_density", 0)
                if r["metrics"].get("diff_CD8_T_density") is not None
                else 0
                for r in pair_data
            ])
        )
    return {
        "title": "CODEX 配对样本空间证据展示系统",
        "claim": "卵巢转移灶中 CD8+T 细胞减少，并伴随局部免疫接触下降",
        "generated_from": "local CODEX object tables and round3 result summaries",
        "pairs": pair_data,
        "defaultPairIndex": default_pair_index,
        "samples": sample_data,
        "statPanels": stat_panels,
        "colors": {
            "Tumor": "#E06A5F",
            "CD8_T": "#2F80ED",
            "B_cell": "#8E6CCB",
            "CAF": "#6FAF8F",
            "PYCR1_CAF": "#E59B45",
            "CLDN18_Tumor": "#D65F5F",
            "Non_CLDN18_Tumor": "#8A8F98",
        },
        "tour": [
            {"title": "全局样本对照", "metric": "CD8_T_density", "roiKey": "overview", "zoom": "global", "types": ["Tumor", "CD8_T"], "text": "先从原发灶与卵巢转移灶的左右空间视图看整体分布差异。"},
            {"title": "CD8+T 整体减少", "metric": "CD8_T_density", "roiKey": "cd8", "zoom": "roi", "types": ["Tumor", "CD8_T"], "text": "自动放大到 CD8 证据区域：该病例中，转移灶 CD8+T 细胞密度低于原发灶。"},
            {"title": "肿瘤周围 CD8 接触减少", "metric": "CLDN18_Tumor_cd8_neighbors_per_tumor", "roiKey": "local_cd8", "zoom": "roi", "types": ["Tumor", "CD8_T", "CLDN18_Tumor"], "text": "自动放大到肿瘤-CD8 局部邻域区域：20μm 指标只表示局部空间接触机会。"},
            {"title": "B 细胞下降", "metric": "B_cell_density", "roiKey": "bcell", "zoom": "roi", "types": ["Tumor", "CD8_T", "B_cell"], "text": "自动放大到 B 细胞辅助证据区域：B 细胞下降用于支持免疫减弱趋势。"},
            {"title": "CLDN18.2 表型变化", "metric": "CLDN18_Tumor_frac", "roiKey": "cldn", "zoom": "roi", "types": ["CLDN18_Tumor", "Non_CLDN18_Tumor", "CD8_T"], "text": "自动放大到 CLDN18.2 表型区域：阳性/阴性肿瘤比例变化用于刻画肿瘤表型重组。"},
            {"title": "PYCR1+CAF 局部联系减弱", "metric": "PYCR1_CAF_near_cd8_frac", "roiKey": "pycr1", "zoom": "roi", "types": ["PYCR1_CAF", "CD8_T", "Tumor"], "text": "自动放大到 PYCR1+CAF 相关区域：这里只作为局部生态位关系观察，不解释为代谢因果机制。"},
            {"title": "三层证据链总结", "metric": "CD8_T_to_tumor", "roiKey": "overview", "zoom": "global", "types": ["Tumor", "CD8_T", "B_cell", "PYCR1_CAF"], "text": "回到全局视野总结：肿瘤表型变化 + 局部环境重组 + 免疫冷化。"},
        ],
    }


def write_site(data: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "data.js").write_text(
        "window.CODEX_EVIDENCE_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    (OUT / "index.html").write_text(HTML, encoding="utf-8")
    (OUT / "README.md").write_text(
        "# CODEX 配对样本空间证据展示系统\n\n"
        "打开方式：\n\n"
        "```bash\n"
        "cd '/Users/jia/Desktop/学习 /毕业设计/结项答辩！/论文/test-2/5_CODEX配对样本空间证据展示系统'\n"
        "python3 -m http.server 8008\n"
        "```\n\n"
        "然后访问：http://127.0.0.1:8008\n\n"
        "也可以直接双击 `index.html` 打开。推荐使用本地服务器方式，截图导出更稳定。\n",
        encoding="utf-8",
    )


HTML = r'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CODEX 配对样本空间证据展示系统</title>
  <script src="./data.js"></script>
  <style>
    :root {
      --bg: #f1f4f7;
      --panel: #ffffff;
      --ink: #17202a;
      --muted: #687586;
      --line: #e2e8ef;
      --blue: #2F80ED;
      --navy: #12345a;
      --shadow: 0 14px 38px rgba(20, 35, 55, .07);
      --radius: 24px;
    }
    * { box-sizing: border-box; }
    html, body { height: 100%; }
    body {
      margin: 0;
      overflow: hidden;
      color: var(--ink);
      font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif;
      background:
        linear-gradient(90deg, rgba(18,52,90,.035) 1px, transparent 1px),
        linear-gradient(180deg, rgba(18,52,90,.035) 1px, transparent 1px),
        linear-gradient(180deg, #fafcff 0%, var(--bg) 100%);
      background-size: 42px 42px, 42px 42px, auto;
    }
    .shell { max-width: 1780px; height: 100vh; margin: 0 auto; padding: 12px 16px; display: grid; grid-template-rows: 68px 76px minmax(0, 1fr) 112px; gap: 10px; overflow: hidden; }
    .hero {
      display: grid; grid-template-columns: minmax(0,1fr) auto; gap: 14px;
      align-items: center; margin-bottom: 0;
      background: rgba(255,255,255,.90);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 10px 14px;
    }
    .hero-main, .hero-aside, .panel, .metric-card, .stat-card {
      background: rgba(255,255,255,.88);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .hero-main { padding: 0; position: relative; overflow: hidden; box-shadow: none; background: transparent; border: 0; border-radius: 0; }
    .hero-main::after {
      content: ""; position: absolute; inset: auto 26px 0 auto; width: 260px; height: 92px;
      background: linear-gradient(90deg, rgba(47,128,237,.08), rgba(18,52,90,.02));
      border-radius: 999px 999px 0 0; filter: blur(2px); pointer-events: none;
    }
    .eyebrow { display: none; }
    h1 { margin: 0 0 3px; font-size: 25px; line-height: 1.06; color: #12263f; letter-spacing: -.025em; }
    .claim { font-size: 14px; color: #0f4c81; font-weight: 900; margin: 0; }
    .claim-sub { display: none; }
    .hero-aside { padding: 0; display: flex; flex-direction: row; justify-content: flex-end; align-items: center; gap: 8px; box-shadow: none; background: transparent; border: 0; border-radius: 0; }
    .tool-title { display: none; }
    .controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
    .control-strip { background: transparent; border: 0; border-radius: 0; padding: 0; }
    select, button, .toggle {
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 12px;
      padding: 7px 10px;
      font: inherit;
      font-size: 13px;
    }
    button { cursor: pointer; font-weight: 800; transition: .16s ease; }
    button:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(20,35,55,.10); }
    button.primary { background: #0F2A4A; color: #fff; border-color: #0F2A4A; box-shadow: none; }
    button.ghost { background: #f5f8fb; }
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 9px; margin-bottom: 0; min-height: 0; }
    .metric-card { padding: 7px 12px; min-height: 0; cursor: pointer; transition: .18s ease; box-shadow: none; border-radius: 14px; overflow: hidden; }
    .metric-card:hover, .metric-card.active { transform: none; border-color: rgba(47,128,237,.48); background: rgba(47,128,237,.045); }
    .metric-title { font-weight: 900; margin-bottom: 5px; color: #1a2d42; font-size: 13px; display: flex; justify-content: space-between; gap: 8px; align-items: center; white-space: nowrap; overflow: hidden; }
    .metric-title .name { overflow: hidden; text-overflow: ellipsis; }
    .trend-chip { flex: 0 0 auto; font-size: 11px; font-weight: 900; }
    .metric-flow { display: flex; align-items: end; gap: 9px; color: var(--muted); font-size: 11px; }
    .metric-flow b { display: block; color: var(--ink); font-size: 16px; margin-top: 0; letter-spacing: -.01em; }
    .metric-arrow { color: #8a98a8; font-size: 15px; padding-bottom: 1px; }
    .trend { margin-top: 0; display: flex; justify-content: space-between; align-items: center; font-size: 11px; }
    .down { color: #1767cf; font-weight: 900; }
    .up { color: #c94d43; font-weight: 900; }
    .flat { color: #5c6875; font-weight: 900; }
    .workspace { display: grid; grid-template-columns: minmax(0, 4fr) minmax(300px, 1fr); gap: 10px; align-items: stretch; min-height: 0; }
    .panel { padding: 16px; }
    .map-stage { min-height: 0; }
    .workspace > .map-stage > .panel { padding: 10px; border-radius: 20px; height: 100%; display: grid; grid-template-rows: auto minmax(0,1fr) auto; gap: 8px; }
    .viewer-head { display: flex; justify-content: space-between; gap: 10px; align-items: center; margin-bottom: 0; min-height: 36px; }
    .viewer-title h2 { margin: 0; font-size: 17px; letter-spacing: -.01em; }
    .viewer-title p { display: none; }
    .stage-conclusion {
      display: none;
      margin: 0 0 10px;
      padding: 10px 14px;
      border: 1px solid rgba(47,128,237,.18);
      border-left: 5px solid var(--blue);
      border-radius: 20px;
      background: linear-gradient(90deg, rgba(47,128,237,.085), rgba(255,255,255,.78));
      box-shadow: none;
    }
    .stage-conclusion .step {
      color: #1767cf;
      font-size: 12px;
      font-weight: 950;
      letter-spacing: .10em;
      text-transform: uppercase;
      margin-bottom: 6px;
    }
    .stage-conclusion h3 {
      margin: 0;
      color: #112f50;
      font-size: 26px;
      line-height: 1.25;
      letter-spacing: -.01em;
    }
    .stage-conclusion p {
      margin: 7px 0 0;
      color: #52677e;
      font-size: 15px;
      line-height: 1.55;
      font-weight: 650;
    }
    .type-toggles { display: flex; flex-wrap: wrap; gap: 7px; justify-content: flex-end; }
    .toggle { display: inline-flex; align-items: center; gap: 7px; padding: 7px 9px; font-size: 12px; user-select: none; background: rgba(255,255,255,.74); }
    .toggle input { accent-color: var(--blue); }
    .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
    .paired-view { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; min-height: 0; }
    .map-card { background: #fbfcfd; border: 1px solid var(--line); border-radius: 18px; padding: 9px; position: relative; overflow: hidden; box-shadow: none; display: grid; grid-template-rows: auto minmax(0,1fr) auto; min-height: 0; }
    .map-label { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-weight: 900; font-size: 15px; }
    canvas.space { width: 100%; height: 100%; min-height: 360px; display: block; background: #f7f9fb; border: 1px solid #dce5ee; border-radius: 14px; cursor: crosshair; }
    .scale { position: absolute; left: 28px; bottom: 28px; font-size: 12px; color: var(--muted); background: rgba(255,255,255,.78); padding: 5px 7px; border-radius: 8px; }
    .map-caption { color: var(--muted); font-size: 12px; margin-top: 5px; line-height: 1.35; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .legend { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 0; color: var(--muted); font-size: 12px; }
    .side { position: static; display: flex; flex-direction: column; gap: 0; min-height: 0; }
    .side h3 { margin: 0 0 10px; font-size: 18px; }
    .kv { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; color: var(--muted); }
    .kv b { display: block; color: var(--ink); font-size: 15px; margin-top: 2px; }
    .evidence-stack { display: grid; gap: 10px; margin-top: 12px; }
    .evidence-block { border: 1px solid var(--line); border-radius: 15px; padding: 11px 12px; background: #f8fafc; }
    .evidence-block strong { display: block; font-size: 12px; color: #52677e; margin-bottom: 5px; letter-spacing: .04em; }
    .evidence-block p { margin: 0; line-height: 1.58; font-weight: 740; color: #193a5a; }
    .evidence-block.boundary { background: #fff8e8; border-color: #f3d99c; }
    .evidence-block.boundary p { color: #76520e; font-weight: 650; }
    .explain { margin-top: 12px; background: #edf6ff; border: 1px solid #cfe3fb; color: #164a7a; border-radius: 14px; padding: 12px; line-height: 1.65; font-weight: 700; }
    .caution { background: #fff8e8; border-color: #f3d99c; color: #76520e; font-weight: 600; }
    .stats { display: grid; grid-template-columns: repeat(7, minmax(0,1fr)); gap: 8px; margin-top: 0; opacity: 1; min-height: 0; }
    .stat-card { padding: 8px; cursor: pointer; box-shadow: none; border-radius: 14px; min-width: 0; display: grid; grid-template-rows: auto minmax(0,1fr) auto; }
    .stat-card.active { outline: 1.5px solid rgba(47,128,237,.65); background: rgba(47,128,237,.045); }
    .stat-card h4 { margin: 0 0 4px; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .stat-card .thumb-direction { color: var(--muted); font-size: 11px; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    canvas.stat { width: 100%; height: 48px; display: block; }
    .tour-box { background: #fff; color: var(--ink); border: 1px solid var(--line); border-radius: 18px; padding: 13px; box-shadow: none; height: 100%; display: flex; flex-direction: column; overflow: auto; }
    .tour-box h3 { color: #0F2A4A; font-size: 20px; margin-bottom: 8px; }
    .tour-box p { color: #26384c; line-height: 1.55; font-weight: 700; }
    .tour-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .tour-actions button { background: #f5f8fb; color: var(--ink); border-color: var(--line); }
    .roi-grid { display: grid; grid-template-columns: repeat(2,1fr); gap: 7px; margin-top: 8px; }
    .roi-pill { background: #f7f9fb; border: 1px solid var(--line); border-radius: 12px; padding: 7px; font-size: 11px; color: var(--muted); }
    .roi-pill b { display: block; color: var(--ink); font-size: 14px; }
    .roi-details { margin-top: 10px; border-top: 1px solid var(--line); padding-top: 10px; }
    .roi-details summary { cursor: pointer; color: #0F2A4A; font-weight: 900; font-size: 13px; }
    @media (max-width: 1200px) {
      body { overflow: auto; }
      .shell { height: auto; min-height: 100vh; overflow: visible; grid-template-rows: auto auto auto auto; }
      .hero, .workspace, .paired-view { grid-template-columns: 1fr; }
      .metric-grid, .stats { grid-template-columns: repeat(2, 1fr); }
      .side { position: static; }
    }
    body.presentation .advanced-control,
    body.presentation .roi-details,
    body.presentation .type-toggles,
    body.presentation .map-caption,
    body.presentation .viewer-title p {
      display: none !important;
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="hero-main">
        <div class="eyebrow">CODEX Paired Spatial Evidence</div>
        <h1>CODEX 配对样本空间证据展示系统</h1>
        <p class="claim">卵巢转移灶中 CD8+T 细胞减少，并伴随局部免疫接触下降</p>
        <p class="claim-sub">以配对空间图为主舞台，串联 CD8 主结论、B 细胞佐证、肿瘤表型变化与局部生态重组证据。</p>
      </div>
      <div class="hero-aside">
        <div class="control-strip">
          <div class="tool-title">Presentation Controls</div>
          <div class="controls">
            <label>配对样本 <select id="pairSelect"></select></label>
            <button class="primary" id="tourStart">开始导览</button>
            <button id="pauseStep">暂停</button>
            <button class="ghost" id="exportBtn">导出 PNG</button>
            <button id="resetView">重置视图</button>
            <button id="presentationMode">展示模式</button>
          </div>
        </div>
        <div class="controls advanced-control">
          <button id="roiMode">显示 ROI 局部</button>
          <label class="toggle"><input type="checkbox" id="showNeighborhood">显示 20μm 邻域圈</label>
        </div>
      </div>
    </section>

    <section class="metric-grid" id="metricCards"></section>

    <main class="workspace">
      <section class="map-stage">
        <div class="panel">
          <div class="viewer-head">
            <div class="viewer-title">
              <h2>Primary vs Metastasis 左右空间对照</h2>
              <p>默认突出 Tumor 与 CD8_T；其他对象按证据链需要打开，避免把空间图变成“彩色噪声”。</p>
            </div>
            <div class="type-toggles" id="typeToggles"></div>
          </div>
          <div class="stage-conclusion">
            <div class="step" id="stageStep">Evidence step</div>
            <h3 id="stageTitle">证据链总览</h3>
            <p id="stageText">系统会按照论文证据链自动巡回导览，并在每一步切换到对应的代表性空间区域。</p>
          </div>
          <div class="paired-view">
            <div class="map-card">
              <div class="map-label"><span>Primary 原发灶</span><span id="primaryCount"></span></div>
              <canvas class="space" id="primaryCanvas"></canvas>
              <div class="scale">比例尺 100μm</div>
              <div class="map-caption" id="primaryCaption"></div>
            </div>
            <div class="map-card">
              <div class="map-label"><span>Metastasis 卵巢转移灶</span><span id="metCount"></span></div>
              <canvas class="space" id="metCanvas"></canvas>
              <div class="scale">比例尺 100μm</div>
              <div class="map-caption" id="metCaption"></div>
            </div>
          </div>
          <div class="legend" id="legend"></div>
        </div>
      </section>

      <aside class="side">
        <div class="tour-box evidence-panel-main">
          <h3 id="tourTitle">证据链导览</h3>
          <p id="tourText">点击“开始自动导览”，系统会按照论文三层证据链自动切换高亮对象和讲解。</p>
          <div class="tour-actions">
            <button id="prevStep">上一步</button>
            <button id="nextStep">下一步</button>
          </div>
          <div class="kv" id="sampleInfo"></div>
          <div class="evidence-stack" id="evidenceSentence"></div>
          <details class="roi-details">
            <summary>展开 ROI 统计</summary>
            <div class="roi-grid" id="roiInfo"></div>
            <div class="explain" id="roiSentence">点击 ROI 或切换 ROI 模式后，查看局部 CD8 接触情况。</div>
          </details>
        </div>
      </aside>
    </main>
    <section class="stats" id="stats"></section>
  </div>

<script>
const DATA = window.CODEX_EVIDENCE_DATA;
const COLORS = DATA.colors;
const DRAW_ORDER = ["Tumor", "Non_CLDN18_Tumor", "CLDN18_Tumor", "CAF", "PYCR1_CAF", "B_cell", "CD8_T"];
const TYPE_LABEL = {
  Tumor: "Tumor", CD8_T: "CD8_T", B_cell: "B_cell", CAF: "CAF",
  PYCR1_CAF: "PYCR1+CAF", CLDN18_Tumor: "CLDN18.2+ Tumor", Non_CLDN18_Tumor: "CLDN18.2- Tumor"
};
const METRIC_LABEL = {
  CD8_T_density: "CD8+T 细胞密度",
  CD8_T_n: "CD8+T 细胞数量",
  CD8_T_to_tumor: "CD8_T/Tumor 比例",
  CLDN18_Tumor_cd8_neighbors_per_tumor: "肿瘤周围 CD8 平均邻居数",
  B_cell_density: "B 细胞密度",
  CLDN18_Tumor_frac: "CLDN18.2 阳性肿瘤比例",
  PYCR1_CAF_near_cd8_frac: "PYCR1+CAF near CD8"
};
let state = {
  pairIndex: DATA.defaultPairIndex || 0,
  visible: new Set(["Tumor", "CD8_T"]),
  activeMetric: "CD8_T_density",
  activeRoiKey: "overview",
  roiMode: false,
  zoom: 1,
  panX: 0,
  panY: 0,
  viewFrom: null,
  viewTo: null,
  viewProgress: 1,
  viewAnim: null,
  selected: null,
  tourIndex: 0,
  tourTimer: null,
  tourPaused: true
};
const TOUR_INTERVAL_MS = 2600;
const el = id => document.getElementById(id);
const pairSelect = el("pairSelect");
const primaryCanvas = el("primaryCanvas");
const metCanvas = el("metCanvas");

function currentPair(){ return DATA.pairs[state.pairIndex]; }
function sample(side){ const p=currentPair(); return DATA.samples[side==="primary" ? p.primary_sample : p.met_sample]; }
function fmt(v){ if(v===null || v===undefined || Number.isNaN(v)) return "NA"; if(Math.abs(v)>=1000) return Number(v).toLocaleString(); return Number(v).toFixed(Math.abs(v)<1 ? 3 : 2).replace(/\.?0+$/,""); }
function rel(v){ return v===null || v===undefined ? "NA" : `${Number(v).toFixed(1)}%`; }
function directionIcon(d){ return d==="down" ? "↓ 下降" : d==="up" ? "↑ 上升" : "→ 持平"; }
function activeRoi(s){
  return (s.rois && s.rois[state.activeRoiKey]) || s.roi || (s.rois && s.rois.overview);
}

function init(){
  DATA.pairs.forEach((p,i)=>{
    const opt=document.createElement("option");
    opt.value=i; opt.textContent=`患者 ${p.patient_id}: ${p.pair_label}`;
    pairSelect.appendChild(opt);
  });
  pairSelect.value = String(state.pairIndex);
  pairSelect.addEventListener("change", e=>{ state.pairIndex=+e.target.value; state.selected=null; renderAll(); });
  el("resetView").onclick=()=>{ state.zoom=1; state.panX=0; state.panY=0; state.selected=null; animateToView("overview", false); };
  el("roiMode").onclick=()=>{ setRoiMode(!state.roiMode, true); };
  el("showNeighborhood").onchange=()=>renderAll();
  el("tourStart").onclick=startTour;
  el("prevStep").onclick=()=>stepTour(-1, true);
  el("nextStep").onclick=()=>stepTour(1, true);
  el("pauseStep").onclick=()=>toggleTourPause();
  el("presentationMode").onclick=()=>togglePresentationMode();
  el("exportBtn").onclick=exportCurrentView;
  buildToggles();
  buildStats();
  bindCanvas(primaryCanvas, "primary");
  bindCanvas(metCanvas, "met");
  renderAll();
  setStageConclusion("Evidence loop", "证据链总览", "系统会自动循环导览每个子结论；如需停留讲解，可点击右侧“暂停”。");
  setTimeout(()=>startTour(), 700);
}

function buildToggles(){
  const box=el("typeToggles");
  box.innerHTML="";
  DRAW_ORDER.forEach(t=>{
    const lab=document.createElement("label");
    lab.className="toggle";
    lab.innerHTML=`<input type="checkbox" ${state.visible.has(t)?"checked":""} data-type="${t}"><span class="dot" style="background:${COLORS[t]}"></span>${TYPE_LABEL[t]}`;
    lab.querySelector("input").onchange=e=>{
      if(e.target.checked) state.visible.add(t); else state.visible.delete(t);
      renderAll();
    };
    box.appendChild(lab);
  });
  el("legend").innerHTML = DRAW_ORDER.map(t=>`<span><span class="dot" style="background:${COLORS[t]}"></span> ${TYPE_LABEL[t]}</span>`).join("");
}

function buildCards(){
  const p=currentPair();
  el("metricCards").innerHTML = p.cards.map(c=>`
    <div class="metric-card ${c.metric===state.activeMetric?"active":""}" data-metric="${c.metric}">
      <div class="metric-title"><span class="name">${c.label}</span><span class="trend-chip ${c.direction}">${directionIcon(c.direction)} ${rel(c.relative_change)}</span></div>
      <div class="metric-flow">
        <span>Primary<b>${fmt(c.primary)}</b></span>
        <span class="metric-arrow">→</span>
        <span>Metastasis<b>${fmt(c.met)}</b></span>
      </div>
    </div>
  `).join("");
  document.querySelectorAll(".metric-card").forEach(card=>{
    card.onclick=()=>{
      state.activeMetric=card.dataset.metric;
      metricToTypes(state.activeMetric);
      const p=currentPair(), c=p.cards.find(x=>x.metric===state.activeMetric);
      setStageConclusion("指标聚焦", c ? c.label : "空间指标", "点击指标卡后，空间图会切换高亮相关对象；该视图用于辅助理解论文证据链。");
      renderAll();
    };
  });
}

function metricToTypes(metric){
  const panel = DATA.statPanels.find(s=>s.id===metric);
  const types = panel ? panel.target : metric.includes("B_cell") ? ["B_cell"] : metric.includes("PYCR1") ? ["PYCR1_CAF","CD8_T"] : ["Tumor","CD8_T"];
  state.visible = new Set(["Tumor", ...types]);
  buildToggles();
}

function buildStats(){
  const stats=el("stats");
  stats.innerHTML = DATA.tour.map((step,i)=>`
    <div class="stat-card" data-tour-index="${i}" data-metric="${step.metric}">
      <h4>${i+1}. ${step.title}</h4>
      <canvas class="stat" id="stat_tour_${i}"></canvas>
      <div class="thumb-direction">${thumbDirection(step.metric)}</div>
    </div>
  `).join("");
  document.querySelectorAll(".stat-card").forEach(c=>{
    c.onclick=()=>{
      state.tourIndex=Number(c.dataset.tourIndex);
      pauseTour(true);
      applyTour();
    };
  });
}

function thumbDirection(metric){
  const card=currentPair().cards.find(c=>c.metric===metric);
  return card ? `${directionIcon(card.direction)} · ${rel(card.relative_change)}` : "空间证据";
}

function setStageConclusion(step, title, text){
  el("stageStep").textContent = step;
  el("stageTitle").textContent = title;
  el("stageText").textContent = text;
}

function drawStats(){
  DATA.tour.forEach((step,i)=>{
    const canvas=el(`stat_tour_${i}`);
    if(!canvas) return;
    const panel=DATA.statPanels.find(p=>p.id===step.metric);
    const dpr=window.devicePixelRatio||1;
    const w=canvas.clientWidth*dpr, h=canvas.clientHeight*dpr;
    canvas.width=w; canvas.height=h;
    const ctx=canvas.getContext("2d"); ctx.clearRect(0,0,w,h); ctx.scale(dpr,dpr);
    if(!panel){
      ctx.fillStyle="#eef3f8"; ctx.fillRect(0,0,canvas.clientWidth,canvas.clientHeight);
      ctx.fillStyle="#6b7c8e"; ctx.font="12px sans-serif"; ctx.fillText("summary", 12, canvas.clientHeight/2+4);
      return;
    }
    const rows=panel.rows.filter(r=>r.primary!==null && r.met!==null);
    const vals=rows.flatMap(r=>[r.primary,r.met]).filter(v=>Number.isFinite(v));
    const min=Math.min(...vals), max=Math.max(...vals);
    const pad=8, W=canvas.clientWidth, H=canvas.clientHeight;
    ctx.strokeStyle="#e3e9f0"; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(12,pad); ctx.lineTo(12,H-pad); ctx.lineTo(W-8,H-pad); ctx.stroke();
    rows.forEach((r,i)=>{
      const y1=scale(r.primary,min,max,H-pad,pad), y2=scale(r.met,min,max,H-pad,pad);
      const x1=24, x2=W-16;
      ctx.strokeStyle="rgba(47,128,237,.24)"; ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
      ctx.fillStyle="#2F80ED"; ctx.beginPath(); ctx.arc(x1,y1,1.8,0,Math.PI*2); ctx.fill();
      ctx.fillStyle="#78A7E8"; ctx.beginPath(); ctx.arc(x2,y2,1.8,0,Math.PI*2); ctx.fill();
    });
  });
  document.querySelectorAll(".stat-card").forEach(c=>c.classList.toggle("active", Number(c.dataset.tourIndex)===state.tourIndex));
  document.querySelectorAll(".thumb-direction").forEach((d,i)=>{ d.textContent=thumbDirection(DATA.tour[i].metric); });
}
function scale(v,min,max,a,b){ if(max===min) return (a+b)/2; return a-(v-min)/(max-min)*(a-b); }
function lerp(a,b,t){ return a + (b-a)*t; }
function easeInOut(t){ return t < .5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2; }
function normBox(box){
  if(box.x0 !== undefined) return {xmin: box.x0, xmax: box.x1, ymin: box.y0, ymax: box.y1};
  return {xmin: box.xmin, xmax: box.xmax, ymin: box.ymin, ymax: box.ymax};
}
function boxFor(s, roiKey=state.activeRoiKey, roiMode=state.roiMode){
  if(!roiMode) return normBox(s.bounds);
  const roi = (s.rois && s.rois[roiKey]) || s.roi || (s.rois && s.rois.overview);
  return normBox(roi);
}
function mixBox(a,b,t){
  return {
    xmin: lerp(a.xmin, b.xmin, t),
    xmax: lerp(a.xmax, b.xmax, t),
    ymin: lerp(a.ymin, b.ymin, t),
    ymax: lerp(a.ymax, b.ymax, t)
  };
}
function currentBox(s, side){
  if(state.viewFrom && state.viewTo && state.viewProgress < 1){
    return mixBox(state.viewFrom[side], state.viewTo[side], easeInOut(state.viewProgress));
  }
  return boxFor(s);
}

function canvasTransform(canvas, s, side){
  const b = currentBox(s, side);
  const rect = canvas.getBoundingClientRect();
  const pad = 18;
  const bw = b.xmax - b.xmin;
  const bh = b.ymax - b.ymin;
  const sx = (rect.width - pad*2) / bw;
  const sy = (rect.height - pad*2) / bh;
  const base = Math.min(sx, sy) * state.zoom;
  const xmin = b.xmin, ymin = b.ymin;
  const cx = rect.width/2 + state.panX;
  const cy = rect.height/2 + state.panY;
  return {base, xmin, ymin, bw, bh, cx, cy, rect};
}
function project(pt, tr){
  const x=(pt.x-tr.xmin-tr.bw/2)*tr.base + tr.cx;
  const y=(pt.y-tr.ymin-tr.bh/2)*tr.base + tr.cy;
  return [x,y];
}
function niceStep(raw){
  const pow = Math.pow(10, Math.floor(Math.log10(raw || 1)));
  const n = raw / pow;
  const m = n <= 1 ? 1 : n <= 2 ? 2 : n <= 5 ? 5 : 10;
  return m * pow;
}
function drawSpatialGrid(ctx, tr, rect){
  const step = niceStep(Math.max(tr.bw, tr.bh) / 7);
  const minor = step / 2;
  ctx.save();
  ctx.lineWidth = 1;
    ctx.strokeStyle = "rgba(31,78,121,.060)";
  for(let x=Math.floor((tr.xmin-tr.bw*.1)/minor)*minor; x<=tr.xmin+tr.bw*1.1; x+=minor){
    const [px0,py0]=project({x, y:tr.ymin-tr.bh*.1},tr);
    const [px1,py1]=project({x, y:tr.ymin+tr.bh*1.1},tr);
    ctx.beginPath(); ctx.moveTo(px0,py0); ctx.lineTo(px1,py1); ctx.stroke();
  }
  for(let y=Math.floor((tr.ymin-tr.bh*.1)/minor)*minor; y<=tr.ymin+tr.bh*1.1; y+=minor){
    const [px0,py0]=project({x:tr.xmin-tr.bw*.1, y},tr);
    const [px1,py1]=project({x:tr.xmin+tr.bw*1.1, y},tr);
    ctx.beginPath(); ctx.moveTo(px0,py0); ctx.lineTo(px1,py1); ctx.stroke();
  }
  ctx.strokeStyle = "rgba(31,78,121,.115)";
  for(let x=Math.floor((tr.xmin-tr.bw*.1)/step)*step; x<=tr.xmin+tr.bw*1.1; x+=step){
    const [px0,py0]=project({x, y:tr.ymin-tr.bh*.1},tr);
    const [px1,py1]=project({x, y:tr.ymin+tr.bh*1.1},tr);
    ctx.beginPath(); ctx.moveTo(px0,py0); ctx.lineTo(px1,py1); ctx.stroke();
  }
  for(let y=Math.floor((tr.ymin-tr.bh*.1)/step)*step; y<=tr.ymin+tr.bh*1.1; y+=step){
    const [px0,py0]=project({x:tr.xmin-tr.bw*.1, y},tr);
    const [px1,py1]=project({x:tr.xmin+tr.bw*1.1, y},tr);
    ctx.beginPath(); ctx.moveTo(px0,py0); ctx.lineTo(px1,py1); ctx.stroke();
  }
  ctx.restore();
}
function drawMiniMap(ctx, s, rect, side){
  const w = 112, h = 94, x0 = 18, y0 = 18;
  const b = s.bounds;
  const bw = b.xmax - b.xmin, bh = b.ymax - b.ymin;
  const scaleMini = Math.min((w - 16) / bw, (h - 22) / bh);
  const ox = x0 + w / 2, oy = y0 + h / 2 + 5;
  const mapPoint = pt => [
    (pt.x - b.xmin - bw / 2) * scaleMini + ox,
    (pt.y - b.ymin - bh / 2) * scaleMini + oy
  ];
  ctx.save();
  ctx.globalAlpha = 1;
  ctx.fillStyle = "rgba(255,255,255,.88)";
  ctx.strokeStyle = "rgba(31,78,121,.28)";
  ctx.lineWidth = 1;
  roundRect(ctx, x0, y0, w, h, 12);
  ctx.fill();
  ctx.stroke();
  ctx.save();
  ctx.beginPath();
  roundRect(ctx, x0 + 7, y0 + 20, w - 14, h - 28, 8);
  ctx.clip();
  ["Tumor", "CD8_T"].forEach(t => {
    ctx.fillStyle = COLORS[t];
    ctx.globalAlpha = t === "Tumor" ? .18 : .55;
    const pts = s.points.filter(p => p.flags.includes(t));
    const step = Math.max(1, Math.ceil(pts.length / 900));
    for (let i = 0; i < pts.length; i += step) {
      const [x, y] = mapPoint(pts[i]);
      ctx.beginPath();
      ctx.arc(x, y, t === "CD8_T" ? 1.15 : .8, 0, Math.PI * 2);
      ctx.fill();
    }
  });
  const viewBox = currentBox(s, side);
  const [rx0, ry0] = mapPoint({x: viewBox.xmin, y: viewBox.ymin});
  const [rx1, ry1] = mapPoint({x: viewBox.xmax, y: viewBox.ymax});
  ctx.globalAlpha = 1;
  ctx.strokeStyle = "#1f4e79";
  ctx.lineWidth = 1.4;
  ctx.setLineDash([4, 3]);
  ctx.strokeRect(rx0, ry0, rx1 - rx0, ry1 - ry0);
  ctx.setLineDash([]);
  ctx.restore();
  ctx.fillStyle = "#1f4e79";
  ctx.font = "bold 11px sans-serif";
  ctx.fillText("全局缩略图 / 当前视野", x0 + 12, y0 + 14);
  ctx.restore();
}
function roundRect(ctx, x, y, w, h, r){
  ctx.beginPath();
  ctx.moveTo(x+r, y);
  ctx.arcTo(x+w, y, x+w, y+h, r);
  ctx.arcTo(x+w, y+h, x, y+h, r);
  ctx.arcTo(x, y+h, x, y, r);
  ctx.arcTo(x, y, x+w, y, r);
  ctx.closePath();
}

function drawSpace(canvas, side){
  const s=sample(side);
  const dpr=window.devicePixelRatio||1;
  const rect=canvas.getBoundingClientRect();
  canvas.width=rect.width*dpr; canvas.height=rect.height*dpr;
  const ctx=canvas.getContext("2d");
  ctx.setTransform(dpr,0,0,dpr,0,0);
  ctx.clearRect(0,0,rect.width,rect.height);
  ctx.fillStyle="#f7f9fb"; ctx.fillRect(0,0,rect.width,rect.height);
  const tr=canvasTransform(canvas,s,side);
  ctx.save();
  drawSpatialGrid(ctx, tr, rect);
  const roi=activeRoi(s);
  DRAW_ORDER.forEach(t=>{
    const pts=s.points.filter(p=>p.type===t || p.flags.includes(t));
    const highlighted = state.visible.has(t);
    const isBackground = t==="Tumor" || t==="Non_CLDN18_Tumor" || t==="CLDN18_Tumor";
    ctx.fillStyle=COLORS[t];
    ctx.globalAlpha = highlighted ? (isBackground ? .32 : .98) : (isBackground ? .05 : .08);
    const radius = highlighted
      ? (t==="CD8_T" ? 3.6 : t==="B_cell" ? 3.0 : t==="PYCR1_CAF" ? 3.25 : 2.1)
      : (t==="CD8_T" ? 1.7 : t==="B_cell" ? 1.5 : 1.25);
    pts.forEach(pt=>{
      const [x,y]=project(pt,tr);
      if(x<-10||y<-10||x>rect.width+10||y>rect.height+10) return;
      if(highlighted && !isBackground){
        ctx.globalAlpha = .20;
        ctx.beginPath(); ctx.arc(x,y,radius+2.4,0,Math.PI*2); ctx.fill();
        ctx.globalAlpha = .98;
      }
      ctx.beginPath(); ctx.arc(x,y,radius,0,Math.PI*2); ctx.fill();
    });
  });
  ctx.globalAlpha=1;
  if(!state.roiMode){
    const [x0,y0]=project({x:roi.x0,y:roi.y0},tr), [x1,y1]=project({x:roi.x1,y:roi.y1},tr);
    ctx.strokeStyle="#1f4e79"; ctx.lineWidth=2; ctx.setLineDash([6,4]);
    ctx.strokeRect(x0,y0,x1-x0,y1-y0); ctx.setLineDash([]);
    ctx.fillStyle="rgba(31,78,121,.08)"; ctx.fillRect(x0,y0,x1-x0,y1-y0);
  }
  if(el("showNeighborhood").checked && state.selected && state.selected.side===side){
    const [x,y]=project(state.selected.pt,tr);
    ctx.strokeStyle="#111"; ctx.lineWidth=1.5; ctx.setLineDash([3,3]);
    ctx.beginPath(); ctx.arc(x,y,20*tr.base,0,Math.PI*2); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle="#111"; ctx.fillText("20μm", x+8, y-8);
    ctx.fillStyle="#2F80ED"; ctx.globalAlpha=.95;
    s.points.filter(p=>p.flags.includes("CD8_T")).forEach(pt=>{
      const dx=pt.x-state.selected.pt.x, dy=pt.y-state.selected.pt.y;
      if(dx*dx+dy*dy<=400){ const [cx,cy]=project(pt,tr); ctx.beginPath(); ctx.arc(cx,cy,5,0,Math.PI*2); ctx.fill(); }
    });
  }
  drawMiniMap(ctx, s, rect, side);
  ctx.restore();
}

function bindCanvas(canvas, side){
  let dragging=false, last=null;
  canvas.addEventListener("wheel", e=>{
    e.preventDefault();
    const factor=e.deltaY<0?1.12:.89;
    state.zoom=Math.max(.6, Math.min(8, state.zoom*factor));
    renderMaps();
  }, {passive:false});
  canvas.addEventListener("mousedown", e=>{ dragging=true; last=[e.clientX,e.clientY]; });
  window.addEventListener("mouseup", ()=>dragging=false);
  window.addEventListener("mousemove", e=>{
    if(!dragging) return;
    state.panX += e.clientX-last[0]; state.panY += e.clientY-last[1]; last=[e.clientX,e.clientY]; renderMaps();
  });
  canvas.addEventListener("click", e=>{
    if(dragging) return;
    const s=sample(side), tr=canvasTransform(canvas,s,side), rect=canvas.getBoundingClientRect();
    const x=e.clientX-rect.left, y=e.clientY-rect.top;
    let best=null, bestD=Infinity;
    s.points.filter(p=>p.flags.includes("Tumor")).forEach(pt=>{
      const [px,py]=project(pt,tr); const d=(px-x)**2+(py-y)**2;
      if(d<bestD){ bestD=d; best=pt; }
    });
    if(best && bestD<900){ state.selected={side, pt:best}; renderAll(); }
  });
}

function renderMaps(){
  drawSpace(primaryCanvas,"primary"); drawSpace(metCanvas,"met");
}
function setRoiMode(next, animated=true){
  if(animated) animateToView(state.activeRoiKey, next);
  else {
    state.roiMode = next;
    el("roiMode").textContent=state.roiMode?"返回全局视图":"显示 ROI 局部";
    renderAll();
  }
}
function animateToView(nextRoiKey, nextRoiMode){
  if(state.viewAnim) cancelAnimationFrame(state.viewAnim);
  const from = { primary: currentBox(sample("primary"), "primary"), met: currentBox(sample("met"), "met") };
  const startKey = state.activeRoiKey;
  const startMode = state.roiMode;
  state.activeRoiKey = nextRoiKey || "overview";
  state.roiMode = !!nextRoiMode;
  const to = { primary: boxFor(sample("primary"), state.activeRoiKey, state.roiMode), met: boxFor(sample("met"), state.activeRoiKey, state.roiMode) };
  state.viewFrom = from;
  state.viewTo = to;
  state.viewProgress = 0;
  el("roiMode").textContent=state.roiMode?"返回全局视图":"显示 ROI 局部";
  const startZoom = state.zoom;
  const startPanX = state.panX;
  const startPanY = state.panY;
  const t0 = performance.now();
  const duration = 980;
  function tick(now){
    const k = Math.min(1, (now - t0) / duration);
    const e = easeInOut(k);
    state.viewProgress = k;
    state.zoom = lerp(startZoom, 1, e);
    state.panX = lerp(startPanX, 0, e);
    state.panY = lerp(startPanY, 0, e);
    renderMaps();
    updateSide();
    if(k < 1) state.viewAnim = requestAnimationFrame(tick);
    else {
      state.viewProgress = 1;
      state.viewAnim = null;
      state.viewFrom = null;
      state.viewTo = null;
      renderAll();
    }
  }
  state.viewAnim = requestAnimationFrame(tick);
}
function renderAll(){
  buildCards(); drawStats(); renderMaps(); updateSide();
  const ps=sample("primary"), ms=sample("met");
  el("primaryCount").textContent=`显示 ${visibleCount(ps).toLocaleString()} 个对象`;
  el("metCount").textContent=`显示 ${visibleCount(ms).toLocaleString()} 个对象`;
  el("primaryCaption").textContent=`样本 ${ps.sample}，${state.roiMode?"ROI 局部视图":"全局视图"}。Tumor 为背景，CD8_T 为核心高亮对象。`;
  el("metCaption").textContent=`样本 ${ms.sample}，${state.roiMode?"ROI 局部视图":"全局视图"}。用于与原发灶进行同一风格的空间对照。`;
}
function visibleCount(s){ return s.points.filter(p=>[...state.visible].some(t=>p.flags.includes(t)||p.type===t)).length; }

function updateSide(){
  const p=currentPair(), ps=sample("primary"), ms=sample("met");
  const card=p.cards.find(c=>c.metric===state.activeMetric) || p.cards[1];
  el("sampleInfo").innerHTML = `
    <span>患者编号<b>${p.patient_id}</b></span>
    <span>配对样本<b>${p.pair_label}</b></span>
    <span>Primary 总细胞<b>${ps.total_cells.toLocaleString()}</b></span>
    <span>Met 总细胞<b>${ms.total_cells.toLocaleString()}</b></span>
    <span>当前指标<b>${METRIC_LABEL[state.activeMetric]||card.label}</b></span>
    <span>高亮对象<b>${[...state.visible].map(t=>TYPE_LABEL[t]).join(" / ")}</b></span>
    <span>Met-Primary<b>${fmt(card.diff)}</b></span>
    <span>相对变化<b>${rel(card.relative_change)}</b></span>`;
  const directionText = card.direction==="down" ? "低于" : card.direction==="up" ? "高于" : "接近";
  el("evidenceSentence").innerHTML = `
    <div class="evidence-block">
      <strong>当前证据</strong>
      <p>该病例中，转移灶 ${card.label} ${directionText}原发灶。</p>
    </div>
    <div class="evidence-block">
      <strong>数据支持</strong>
      <p>Primary ${fmt(card.primary)} → Metastasis ${fmt(card.met)}；Met-Primary 为 ${fmt(card.diff)}，相对变化 ${rel(card.relative_change)}。</p>
    </div>
    <div class="evidence-block boundary">
      <strong>表述边界</strong>
      <p>该展示用于组织论文证据链和空间直观说明，不单独作为机制证明。20μm 表示局部空间接触机会，不等同于真实细胞相互作用。</p>
    </div>`;
  const r1=activeRoi(ps).metrics, r2=activeRoi(ms).metrics;
  el("roiInfo").innerHTML = ["Tumor","CD8_T","B_cell","PYCR1_CAF","CLDN18_Tumor","Non_CLDN18_Tumor","tumor_cd8_neighbors20"].map(k=>`
    <div class="roi-pill">${k==="tumor_cd8_neighbors20"?"Tumor周围CD8均邻居数":TYPE_LABEL[k]||k}
      <b>${fmt(r1[k])} / ${fmt(r2[k])}</b><span>Primary / Met</span></div>`).join("");
  const roiName = {
    overview: "全局概览 ROI",
    cd8: "CD8 证据 ROI",
    local_cd8: "肿瘤-CD8 局部邻域 ROI",
    bcell: "B 细胞辅助证据 ROI",
    cldn: "CLDN18.2 表型 ROI",
    pycr1: "PYCR1+CAF 局部联系 ROI"
  }[state.activeRoiKey] || "当前 ROI";
  el("roiSentence").textContent = `${roiName} 用于帮助理解当前导览步骤的局部证据；表述保持为“局部 CD8 接触减少”或“局部关系减弱”，不写成机制证明。`;
}

function startTour(){
  pauseTour(false); state.tourIndex=0; applyTour();
  state.tourTimer=setInterval(()=>stepTour(1,false),TOUR_INTERVAL_MS);
  state.tourPaused=false;
  el("pauseStep").textContent="暂停";
}
function pauseTour(markPaused=true){
  if(state.tourTimer){ clearInterval(state.tourTimer); state.tourTimer=null; }
  if(markPaused){
    state.tourPaused=true;
    el("pauseStep").textContent="继续";
  }
}
function resumeTour(){
  if(state.tourTimer) return;
  state.tourPaused=false;
  el("pauseStep").textContent="暂停";
  state.tourTimer=setInterval(()=>stepTour(1,false),TOUR_INTERVAL_MS);
}
function toggleTourPause(){
  if(state.tourPaused) resumeTour();
  else pauseTour(true);
}
function togglePresentationMode(){
  document.body.classList.toggle("presentation");
  const active=document.body.classList.contains("presentation");
  el("presentationMode").textContent=active ? "退出展示" : "展示模式";
  setTimeout(()=>renderMaps(), 80);
}
function stepTour(delta, manual){
  if(manual) pauseTour(true);
  state.tourIndex=(state.tourIndex+delta+DATA.tour.length)%DATA.tour.length; applyTour();
}
function applyTour(){
  const step=DATA.tour[state.tourIndex];
  el("tourTitle").textContent=`${state.tourIndex+1}/${DATA.tour.length} ${step.title}`;
  el("tourText").textContent=step.text;
  setStageConclusion(`Evidence ${state.tourIndex+1}/${DATA.tour.length}`, step.title, step.text);
  state.activeMetric=step.metric; state.visible=new Set(step.types); buildToggles();
  const shouldRoi = step.zoom === "roi";
  buildCards();
  drawStats();
  animateToView(step.roiKey || "overview", shouldRoi);
}

function exportCurrentView(){
  const W=1500,H=980, c=document.createElement("canvas"); c.width=W; c.height=H;
  const ctx=c.getContext("2d");
  ctx.fillStyle="#f7f9fb"; ctx.fillRect(0,0,W,H);
  ctx.fillStyle="#12263f"; ctx.font="bold 34px sans-serif"; ctx.fillText(DATA.title,40,58);
  ctx.fillStyle="#0f4c81"; ctx.font="bold 24px sans-serif"; ctx.fillText(DATA.claim,40,96);
  ctx.drawImage(primaryCanvas,40,150,660,520);
  ctx.drawImage(metCanvas,800,150,660,520);
  ctx.fillStyle="#17202a"; ctx.font="bold 22px sans-serif"; ctx.fillText(`Primary ${sample("primary").sample}`,40,135); ctx.fillText(`Metastasis ${sample("met").sample}`,800,135);
  ctx.font="18px sans-serif"; ctx.fillStyle="#687586";
  const p=currentPair(), card=p.cards.find(c=>c.metric===state.activeMetric)||p.cards[1];
  ctx.fillText(`当前指标：${card.label} | Primary ${fmt(card.primary)} / Met ${fmt(card.met)} / 相对变化 ${rel(card.relative_change)}`,40,720);
  ctx.fillText("20μm 邻域表示局部空间接触机会，不等同于证明真实细胞相互作用。",40,752);
  let x=40,y=804; DRAW_ORDER.forEach(t=>{ if(!state.visible.has(t)) return; ctx.fillStyle=COLORS[t]; ctx.beginPath(); ctx.arc(x,y-5,7,0,Math.PI*2); ctx.fill(); ctx.fillStyle="#17202a"; ctx.fillText(TYPE_LABEL[t],x+14,y); x+=160; });
  const a=document.createElement("a");
  a.download=`CODEX_pair_evidence_${p.pair_label.replaceAll(" ","_")}.png`;
  a.href=c.toDataURL("image/png");
  a.click();
}

init();
</script>
</body>
</html>
'''


def main():
    data = build_data()
    write_site(data)
    print(f"Website generated: {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
