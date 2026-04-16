from pathlib import Path

import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.spatial import cKDTree
from scipy.stats import wilcoxon
import shutil


PAIR_MANIFEST_PATH = Path("/Users/jia/Desktop/学习 /毕业设计/实验/CODEX_clean_baseline/pair_manifest.tsv")
OUT_DIR = Path("/Users/jia/Desktop/学习 /毕业设计/实验/CODEX_baseline_conclusion_visuals")
SUMMARY_PATH = OUT_DIR / "r_only_summary.tsv"
SIGNIFICANCE_PATH = OUT_DIR / "paired_significance.tsv"

plt.rcParams["axes.unicode_minus"] = False

PRIMARY_COLOR = "#2B6CB0"
MET_COLOR = "#C53030"
ACCENT_COLOR = "#2F855A"
LIGHT_BLUE = "#D9E8F5"
LIGHT_RED = "#F7D6D6"


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
    tree = cKDTree(tgt_coords)
    distances, _ = tree.query(src_coords, k=1)
    distances = np.asarray(distances, dtype=float)
    return float(np.mean(distances <= radius))


def avg_count_within_radius(center_coords: np.ndarray, target_coords: np.ndarray, radius: float) -> float:
    if len(center_coords) == 0 or len(target_coords) == 0:
        return np.nan
    tree = cKDTree(target_coords)
    counts = tree.query_ball_point(center_coords, r=radius, return_length=True)
    return float(np.mean(np.asarray(counts, dtype=float)))


def nearest_distances(src_coords: np.ndarray, tgt_coords: np.ndarray) -> np.ndarray:
    if len(src_coords) == 0 or len(tgt_coords) == 0:
        return np.array([], dtype=float)
    tree = cKDTree(tgt_coords)
    distances, _ = tree.query(src_coords, k=1)
    distances = np.asarray(distances, dtype=float)
    return distances[np.isfinite(distances)]


def load_sample_metrics(sample_path: Path) -> dict:
    df = pd.read_csv(sample_path, sep="\t")

    tumor_coords = get_coords(df, "Tumor")
    m1_coords = get_coords(df, "M1")
    m2_coords = get_coords(df, "M2")

    tumor_n = len(tumor_coords)
    m1_n = len(m1_coords)
    m2_n = len(m2_coords)
    m2_frac = safe_div(m2_n, m1_n + m2_n)
    enrich_30_tumor_m1 = avg_count_within_radius(tumor_coords, m1_coords, 30)
    within_20_m2 = within_r_ratio(m2_coords, tumor_coords, 20)
    within_30_m2 = within_r_ratio(m2_coords, tumor_coords, 30)
    m2_distances = nearest_distances(m2_coords, tumor_coords)

    return {
        "tumor_n": tumor_n,
        "m1_n": m1_n,
        "m2_n": m2_n,
        "m2_frac_of_mac": m2_frac,
        "enrich_30_Tumor_M1": enrich_30_tumor_m1,
        "within_20_M2": within_20_m2,
        "within_30_M2": within_30_m2,
        "m2_distance_median": float(np.median(m2_distances)) if len(m2_distances) else np.nan,
        "m2_distances": m2_distances,
    }


def format_value(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def rounded_export_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if pd.api.types.is_numeric_dtype(out[col]):
            out[col] = out[col].round(2)
    return out


def patient_sort_key(sample_name: str) -> tuple[int, str]:
    digits = "".join(ch for ch in str(sample_name) if ch.isdigit())
    return (int(digits) if digits else 9999, str(sample_name))


def build_summary() -> pd.DataFrame:
    pairs = pd.read_csv(PAIR_MANIFEST_PATH, sep="\t")
    r_pairs = pairs[pairs["met_suffix"] == "R"].copy()
    r_pairs = r_pairs.sort_values(["patient_id", "met_sample"]).reset_index(drop=True)

    rows = []
    for _, row in r_pairs.iterrows():
        primary_metrics = load_sample_metrics(Path(row["primary_analysis_path"]))
        met_metrics = load_sample_metrics(Path(row["met_analysis_path"]))

        rows.append(
            {
                "patient_id": int(row["patient_id"]),
                "primary_sample": row["primary_sample"],
                "met_sample": row["met_sample"],
                "pair_label": f'{row["primary_sample"]} vs {row["met_sample"]}',
                "primary_m2_frac_of_mac": primary_metrics["m2_frac_of_mac"],
                "met_m2_frac_of_mac": met_metrics["m2_frac_of_mac"],
                "diff_m2_frac_of_mac": met_metrics["m2_frac_of_mac"] - primary_metrics["m2_frac_of_mac"],
                "primary_enrich_30_Tumor_M1": primary_metrics["enrich_30_Tumor_M1"],
                "met_enrich_30_Tumor_M1": met_metrics["enrich_30_Tumor_M1"],
                "diff_enrich_30_Tumor_M1": met_metrics["enrich_30_Tumor_M1"] - primary_metrics["enrich_30_Tumor_M1"],
                "primary_within_20_M2": primary_metrics["within_20_M2"],
                "met_within_20_M2": met_metrics["within_20_M2"],
                "diff_within_20_M2": met_metrics["within_20_M2"] - primary_metrics["within_20_M2"],
                "primary_within_30_M2": primary_metrics["within_30_M2"],
                "met_within_30_M2": met_metrics["within_30_M2"],
                "diff_within_30_M2": met_metrics["within_30_M2"] - primary_metrics["within_30_M2"],
                "primary_m2_distance_median": primary_metrics["m2_distance_median"],
                "met_m2_distance_median": met_metrics["m2_distance_median"],
                "primary_tumor_n": primary_metrics["tumor_n"],
                "met_tumor_n": met_metrics["tumor_n"],
                "primary_m1_n": primary_metrics["m1_n"],
                "met_m1_n": met_metrics["m1_n"],
                "primary_m2_n": primary_metrics["m2_n"],
                "met_m2_n": met_metrics["m2_n"],
                "primary_m2_distances": primary_metrics["m2_distances"],
                "met_m2_distances": met_metrics["m2_distances"],
            }
        )

    return pd.DataFrame(rows)


def annotate_line_point(ax, x: float, y: float, text: str, color: str, dy: float) -> None:
    ax.annotate(
        text,
        xy=(x, y),
        xytext=(x + 0.02, y + dy),
        textcoords="data",
        fontsize=8.5,
        color=color,
        ha="left",
        va="center",
        arrowprops={"arrowstyle": "-", "color": color, "lw": 0.8},
    )


def make_m2_fraction_figure_all_groups() -> None:
    pairs = pd.read_csv(PAIR_MANIFEST_PATH, sep="\t")
    subset_map = {
        "R样本": pairs[pairs["met_suffix"] == "R"].copy(),
        "L样本": pairs[pairs["met_suffix"] == "L"].copy(),
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.8), sharey=True)

    for ax, (title, sub_df) in zip(axes, subset_map.items()):
        sub_df = sub_df.sort_values(["patient_id", "met_sample"]).reset_index(drop=True)
        x = np.arange(len(sub_df))
        primary_vals = []
        met_vals = []
        labels = []

        for _, row in sub_df.iterrows():
            primary_metrics = load_sample_metrics(Path(row["primary_analysis_path"]))
            met_metrics = load_sample_metrics(Path(row["met_analysis_path"]))
            primary_vals.append(primary_metrics["m2_frac_of_mac"])
            met_vals.append(met_metrics["m2_frac_of_mac"])
            labels.append(str(row["patient_id"]))

        ax.plot(x, primary_vals, color=PRIMARY_COLOR, marker="o", linewidth=2.0, label="原发灶")
        ax.plot(x, met_vals, color=MET_COLOR, marker="o", linewidth=2.0, label="转移灶")

        for xi, pv, mv in zip(x, primary_vals, met_vals):
            ax.annotate(format_value(pv), (xi, pv), textcoords="offset points", xytext=(-10, 8), fontsize=8.5, color=PRIMARY_COLOR)
            ax.annotate(format_value(mv), (xi, mv), textcoords="offset points", xytext=(-10, -14), fontsize=8.5, color=MET_COLOR)

        diffs = np.asarray(met_vals, dtype=float) - np.asarray(primary_vals, dtype=float)
        ax.set_title(f"{title}：m2 / (m1 + m2)", fontsize=13)
        ax.set_xticks(x, labels)
        ax.set_xlabel("样本序号")
        ax.set_ylim(0, 1.08)
        ax.set_ylabel("M2 / (M1 + M2)")
        ax.grid(axis="y", linestyle="--", alpha=0.25)
        ax.text(
            0.02,
            0.96,
            f"转移更高: {(diffs > 0).sum()} / {len(diffs)}\n平均差值: {np.nanmean(diffs):.2f}",
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=9.5,
            color=ACCENT_COLOR,
            bbox={"facecolor": "white", "edgecolor": "#DDDDDD", "alpha": 0.9},
        )

    legend_handles = [
        Line2D([0], [0], color=PRIMARY_COLOR, marker="o", lw=2.0, label="原发灶"),
        Line2D([0], [0], color=MET_COLOR, marker="o", lw=2.0, label="转移灶"),
    ]
    fig.suptitle("结论1：不同转移部位中M2型构成变化", fontsize=16, y=0.98)
    fig.legend(handles=legend_handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.92))
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(OUT_DIR / "结论1_R和L样本_M2巨噬比例.png", dpi=300)
    plt.close(fig)


def make_tumor_m1_pie_figure(summary_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(len(summary_df), 2, figsize=(10.5, 3.2 * len(summary_df)))
    if len(summary_df) == 1:
        axes = np.array([axes])

    for idx, (_, row) in enumerate(summary_df.iterrows()):
        pair_total = np.nansum([row["primary_enrich_30_Tumor_M1"], row["met_enrich_30_Tumor_M1"]])
        for col_idx, prefix in enumerate(["primary", "met"]):
            ax = axes[idx, col_idx]
            tumor_n = row[f"{prefix}_tumor_n"]
            m1_n = row[f"{prefix}_m1_n"]
            other_n = max(tumor_n - m1_n, 0)
            pie_values = np.array([m1_n, other_n], dtype=float)
            pie_colors = [ACCENT_COLOR, "#E5E7EB"]

            if np.isclose(pie_values.sum(), 0):
                ax.text(0.5, 0.5, "无可绘制数据", ha="center", va="center", fontsize=11)
                ax.axis("off")
                continue

            ax.pie(
                pie_values,
                colors=pie_colors,
                startangle=90,
                counterclock=False,
                wedgeprops={"edgecolor": "white"},
            )
            role_cn = "原发灶" if prefix == "primary" else "转移灶"
            enrich_value = row[f"{prefix}_enrich_30_Tumor_M1"]
            ax.set_title(f"患者{row['patient_id']} {role_cn}", fontsize=11)
            ax.text(0, 0, f"M1\n{int(m1_n)}", ha="center", va="center", fontsize=10)
            ax.text(
                0,
                -1.25,
                f"Tumor-M1互作={format_value(enrich_value)}\n"
                f"M1/Tumor={format_value(safe_div(m1_n, tumor_n), 2)}",
                ha="center",
                va="center",
                fontsize=9,
                color=PRIMARY_COLOR if prefix == "primary" else MET_COLOR,
            )
            if col_idx == 0:
                ax.text(
                    -1.55,
                    1.28,
                    row["pair_label"],
                    fontsize=11,
                    ha="left",
                    va="center",
                    color="#222222",
                )
                if not pd.isna(pair_total):
                    ax.text(
                        -1.55,
                        1.02,
                        f"差值(转-原)={format_value(row['diff_enrich_30_Tumor_M1'])}",
                        fontsize=9,
                        ha="left",
                        va="center",
                        color=ACCENT_COLOR,
                    )

    legend_handles = [
        Patch(facecolor=ACCENT_COLOR, label="M1细胞数"),
        Patch(facecolor="#E5E7EB", label="其余Tumor背景"),
    ]
    fig.suptitle("结论2：R样本对中Tumor-M1互作与M1稀少现象", fontsize=16, y=0.995)
    fig.legend(handles=legend_handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.975))
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    fig.savefig(OUT_DIR / "结论2_R样本对_Tumor_M1互作饼图.png", dpi=300)
    plt.close(fig)


def make_m2_outer_box_figure(summary_df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(3, 3, figsize=(14, 11))
    axes = axes.flatten()

    for ax, (_, row) in zip(axes, summary_df.iterrows()):
        primary_dist = np.asarray(row["primary_m2_distances"], dtype=float)
        met_dist = np.asarray(row["met_m2_distances"], dtype=float)

        bp = ax.boxplot(
            [primary_dist, met_dist],
            labels=["原发灶", "转移灶"],
            widths=0.55,
            patch_artist=True,
            showfliers=False,
            medianprops={"color": "#111111", "linewidth": 1.5},
        )
        bp["boxes"][0].set(facecolor=LIGHT_BLUE, edgecolor=PRIMARY_COLOR, linewidth=1.2)
        bp["boxes"][1].set(facecolor=LIGHT_RED, edgecolor=MET_COLOR, linewidth=1.2)
        for whisker in bp["whiskers"]:
            whisker.set(color="#666666", linewidth=1.0)
        for cap in bp["caps"]:
            cap.set(color="#666666", linewidth=1.0)

        p_med = float(np.median(primary_dist)) if len(primary_dist) else np.nan
        m_med = float(np.median(met_dist)) if len(met_dist) else np.nan
        ymax = max(np.nanmax(primary_dist) if len(primary_dist) else 0, np.nanmax(met_dist) if len(met_dist) else 0)
        ax.text(1, p_med, f"中位数={format_value(p_med, 2)}", color=PRIMARY_COLOR, fontsize=8.5, ha="center", va="bottom")
        ax.text(2, m_med, f"中位数={format_value(m_med, 2)}", color=MET_COLOR, fontsize=8.5, ha="center", va="bottom")
        ax.text(
            1.5,
            ymax * 1.06 if ymax > 0 else 1,
            f"within_20_M2: {format_value(row['primary_within_20_M2'])} -> {format_value(row['met_within_20_M2'])}",
            fontsize=8.8,
            color=ACCENT_COLOR,
            ha="center",
            va="bottom",
        )
        ax.set_title(f"患者{row['patient_id']}：{row['pair_label']}", fontsize=11)
        ax.set_ylabel("M2到最近Tumor距离")
        ax.grid(axis="y", linestyle="--", alpha=0.25)

    for ax in axes[len(summary_df):]:
        ax.axis("off")

    legend_handles = [
        Patch(facecolor=LIGHT_BLUE, edgecolor=PRIMARY_COLOR, label="原发灶M2距离分布"),
        Patch(facecolor=LIGHT_RED, edgecolor=MET_COLOR, label="转移灶M2距离分布"),
    ]
    fig.suptitle("结论3：R样本对中M2更外围化而不是更贴Tumor", fontsize=16, y=0.98)
    fig.legend(handles=legend_handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.94))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(OUT_DIR / "结论3_R样本对_M2外围化箱线图.png", dpi=300)
    plt.close(fig)


def print_terminal_summary(summary_df: pd.DataFrame) -> None:
    print("\n===== R-only 7对样本摘要 =====")
    display_cols = [
        "pair_label",
        "primary_m2_frac_of_mac",
        "met_m2_frac_of_mac",
        "diff_m2_frac_of_mac",
        "primary_enrich_30_Tumor_M1",
        "met_enrich_30_Tumor_M1",
        "diff_enrich_30_Tumor_M1",
        "primary_within_20_M2",
        "met_within_20_M2",
        "diff_within_20_M2",
        "primary_within_30_M2",
        "met_within_30_M2",
        "diff_within_30_M2",
    ]
    print(summary_df[display_cols].round(2).to_string(index=False))

    print("\n===== 三个结论的总体方向 =====")
    print(
        "结论1 M2/巨噬比例: "
        f"7对中有 {(summary_df['diff_m2_frac_of_mac'] > 0).sum()} 对转移灶更高, "
        f"平均差值={summary_df['diff_m2_frac_of_mac'].mean():.2f}, "
        f"中位差值={summary_df['diff_m2_frac_of_mac'].median():.2f}"
    )
    print(
        "结论2 Tumor-M1互作(30): "
        f"7对中有 {(summary_df['diff_enrich_30_Tumor_M1'] < 0).sum()} 对转移灶更低, "
        f"平均差值={summary_df['diff_enrich_30_Tumor_M1'].mean():.2f}, "
        f"中位差值={summary_df['diff_enrich_30_Tumor_M1'].median():.2f}"
    )
    print(
        "结论3 M2贴Tumor比例: "
        f"within_20_M2 平均差值={summary_df['diff_within_20_M2'].mean():.2f}, "
        f"中位差值={summary_df['diff_within_20_M2'].median():.2f}; "
        f"within_30_M2 平均差值={summary_df['diff_within_30_M2'].mean():.2f}, "
        f"中位差值={summary_df['diff_within_30_M2'].median():.2f}"
    )


def paired_wilcoxon(values: pd.Series) -> tuple[float, int]:
    x = values.dropna().to_numpy(dtype=float)
    if len(x) < 2:
        return np.nan, len(x)
    try:
        return float(wilcoxon(x, zero_method="pratt").pvalue), len(x)
    except Exception:
        return np.nan, len(x)


def build_significance_table() -> pd.DataFrame:
    pairs = pd.read_csv(PAIR_MANIFEST_PATH, sep="\t")
    rows = []
    for group in ["R", "L", "QT"]:
        group_pairs = pairs[pairs["met_suffix"] == group].copy()
        if group_pairs.empty:
            continue

        group_rows = []
        for _, row in group_pairs.iterrows():
            primary_metrics = load_sample_metrics(Path(row["primary_analysis_path"]))
            met_metrics = load_sample_metrics(Path(row["met_analysis_path"]))
            group_rows.append(
                {
                    "diff_m2_frac_of_mac": met_metrics["m2_frac_of_mac"] - primary_metrics["m2_frac_of_mac"],
                    "diff_enrich_30_Tumor_M1": met_metrics["enrich_30_Tumor_M1"] - primary_metrics["enrich_30_Tumor_M1"]
                    if pd.notna(primary_metrics["enrich_30_Tumor_M1"]) and pd.notna(met_metrics["enrich_30_Tumor_M1"])
                    else np.nan,
                    "diff_within_20_M2": met_metrics["within_20_M2"] - primary_metrics["within_20_M2"]
                    if pd.notna(primary_metrics["within_20_M2"]) and pd.notna(met_metrics["within_20_M2"])
                    else np.nan,
                    "diff_within_30_M2": met_metrics["within_30_M2"] - primary_metrics["within_30_M2"]
                    if pd.notna(primary_metrics["within_30_M2"]) and pd.notna(met_metrics["within_30_M2"])
                    else np.nan,
                }
            )

        diff_df = pd.DataFrame(group_rows)
        for metric_col in diff_df.columns:
            p_value, n_pairs = paired_wilcoxon(diff_df[metric_col])
            rows.append(
                {
                    "group": group,
                    "metric": metric_col,
                    "n_pairs": n_pairs,
                    "mean_diff": round(float(diff_df[metric_col].dropna().mean()), 2) if diff_df[metric_col].dropna().size else np.nan,
                    "median_diff": round(float(diff_df[metric_col].dropna().median()), 2) if diff_df[metric_col].dropna().size else np.nan,
                    "wilcoxon_p": round(p_value, 4) if pd.notna(p_value) else np.nan,
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_df = build_summary()
    summary_df = summary_df.sort_values("primary_sample", key=lambda s: s.map(patient_sort_key)).reset_index(drop=True)
    export_df = rounded_export_df(summary_df.drop(columns=["primary_m2_distances", "met_m2_distances"]))
    export_df.to_csv(SUMMARY_PATH, sep="\t", index=False)

    make_m2_fraction_figure_all_groups()
    make_tumor_m1_pie_figure(summary_df)
    make_m2_outer_box_figure(summary_df)
    significance_df = build_significance_table()
    significance_df.to_csv(SIGNIFICANCE_PATH, sep="\t", index=False)
    print_terminal_summary(summary_df)

    print("\n输出文件：")
    print(OUT_DIR / "结论1_R和L样本_M2巨噬比例.png")
    print(OUT_DIR / "结论2_R样本对_Tumor_M1互作饼图.png")
    print(OUT_DIR / "结论3_R样本对_M2外围化箱线图.png")
    print(SUMMARY_PATH)
    print(SIGNIFICANCE_PATH)


if __name__ == "__main__":
    main()
