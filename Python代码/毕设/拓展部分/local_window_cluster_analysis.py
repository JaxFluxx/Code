from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["PingFang SC", "Arial Unicode MS", "Heiti SC", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

PAIR_MANIFEST = Path("/Users/jia/Desktop/学习 /毕业设计/实验/CODEX_clean_baseline/pair_manifest.tsv")
OUTPUT_DIR = Path("/Users/jia/Desktop/学习 /毕业设计/实验/拓展部分_局部窗口聚类")
TABLE_DIR = OUTPUT_DIR / "tables"
FIG_DIR = OUTPUT_DIR / "figures"

GRID_SIZE = 6
MIN_TOTAL_CELLS = 40
MIN_TUMOR_CELLS = 12
N_CLUSTERS = 4
SEED = 7

FEATURE_COLUMNS = [
    "tumor_density",
    "mac_density",
    "m1_to_tumor",
    "m2_to_tumor",
    "m2_mac_ratio",
    "m2_outer_bias",
    "m1_minus_m2",
]

CLUSTER_COLORS = ["#305f52", "#df5a43", "#187795", "#dc9b1f", "#6d5ab3", "#7c8a3e"]


def ensure_dirs() -> None:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)


def load_pairs() -> list[dict]:
    with PAIR_MANIFEST.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_points(path: str) -> pd.DataFrame:
    usecols = ["Center X", "Center Y", "cell_type"]
    df = pd.read_csv(path, sep="\t", usecols=usecols)
    df = df[df["cell_type"].isin(["Tumor", "M1", "M2"])].copy()
    if df.empty:
        return df
    min_x, max_x = df["Center X"].min(), df["Center X"].max()
    min_y, max_y = df["Center Y"].min(), df["Center Y"].max()
    width = max(max_x - min_x, 1.0)
    height = max(max_y - min_y, 1.0)
    df["nx"] = (df["Center X"] - min_x) / width
    df["ny"] = (df["Center Y"] - min_y) / height
    df["grid_x"] = np.minimum((df["nx"] * GRID_SIZE).astype(int), GRID_SIZE - 1)
    df["grid_y"] = np.minimum((df["ny"] * GRID_SIZE).astype(int), GRID_SIZE - 1)
    return df


def compute_window_features(df: pd.DataFrame, patient_id: str, sample_name: str, sample_role: str, met_suffix: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    grouped = (
        df.groupby(["grid_y", "grid_x", "cell_type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    for col in ["Tumor", "M1", "M2"]:
        if col not in grouped.columns:
            grouped[col] = 0

    grouped["sample_name"] = sample_name
    grouped["patient_id"] = patient_id
    grouped["sample_role"] = sample_role
    grouped["met_suffix"] = met_suffix
    grouped["window_id"] = grouped.apply(lambda r: f"{sample_name}_r{int(r['grid_y'])}_c{int(r['grid_x'])}", axis=1)
    grouped["total_cells"] = grouped["Tumor"] + grouped["M1"] + grouped["M2"]
    grouped["mac_cells"] = grouped["M1"] + grouped["M2"]
    grouped["tumor_density"] = grouped["Tumor"] / grouped["total_cells"].replace(0, np.nan)
    grouped["mac_density"] = grouped["mac_cells"] / grouped["total_cells"].replace(0, np.nan)
    grouped["m1_to_tumor"] = grouped["M1"] / grouped["Tumor"].replace(0, np.nan)
    grouped["m2_to_tumor"] = grouped["M2"] / grouped["Tumor"].replace(0, np.nan)
    grouped["m2_mac_ratio"] = grouped["M2"] / grouped["mac_cells"].replace(0, np.nan)
    grouped["m2_outer_bias"] = grouped["m2_mac_ratio"].fillna(0) - grouped["m2_to_tumor"].fillna(0)
    grouped["m1_minus_m2"] = grouped["m1_to_tumor"].fillna(0) - grouped["m2_to_tumor"].fillna(0)
    grouped["window_cx"] = (grouped["grid_x"] + 0.5) / GRID_SIZE
    grouped["window_cy"] = (grouped["grid_y"] + 0.5) / GRID_SIZE
    grouped = grouped.replace([np.inf, -np.inf], np.nan).fillna(0)
    grouped = grouped[(grouped["total_cells"] >= MIN_TOTAL_CELLS) & (grouped["Tumor"] >= MIN_TUMOR_CELLS)].copy()
    return grouped


def build_window_table() -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for row in load_pairs():
        primary_df = load_points(row["primary_analysis_path"])
        met_df = load_points(row["met_analysis_path"])
        frames.append(compute_window_features(primary_df, row["patient_id"], row["primary_sample"], "Primary", row["met_suffix"]))
        frames.append(compute_window_features(met_df, row["patient_id"], row["met_sample"], "Metastasis", row["met_suffix"]))
    windows = pd.concat(frames, ignore_index=True)
    return windows


def standardize(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = values.mean(axis=0)
    std = values.std(axis=0)
    std[std == 0] = 1.0
    return (values - mean) / std, mean, std


def run_pca(values: np.ndarray, n_components: int = 2) -> tuple[np.ndarray, np.ndarray]:
    centered = values - values.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(centered, full_matrices=False)
    components = vt[:n_components]
    scores = centered @ components.T
    return scores, components


def init_kmeans_pp(values: np.ndarray, n_clusters: int, rng: np.random.Generator) -> np.ndarray:
    centroids = [values[rng.integers(0, len(values))]]
    while len(centroids) < n_clusters:
        distances = np.min([np.sum((values - c) ** 2, axis=1) for c in centroids], axis=0)
        probs = distances / distances.sum() if distances.sum() else np.full(len(values), 1 / len(values))
        centroids.append(values[rng.choice(len(values), p=probs)])
    return np.array(centroids)


def run_kmeans(values: np.ndarray, n_clusters: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    centroids = init_kmeans_pp(values, n_clusters, rng)
    labels = np.zeros(len(values), dtype=int)
    for _ in range(80):
        distances = np.stack([np.sum((values - centroid) ** 2, axis=1) for centroid in centroids], axis=1)
        new_labels = distances.argmin(axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        new_centroids = []
        for i in range(n_clusters):
            members = values[labels == i]
            if len(members) == 0:
                new_centroids.append(values[rng.integers(0, len(values))])
            else:
                new_centroids.append(members.mean(axis=0))
        centroids = np.array(new_centroids)
    return labels, centroids


def describe_cluster(row: pd.Series) -> str:
    if row["m1_to_tumor"] >= row["m2_to_tumor"] and row["m1_to_tumor"] >= 0.18:
        return "Tumor-M1 support"
    if row["m2_mac_ratio"] >= 0.65 and row["m2_outer_bias"] >= 0.25:
        return "M2 outer-biased"
    if row["mac_density"] >= 0.55 and row["m2_to_tumor"] >= 1.0:
        return "Immune-rich M2-skewed"
    if row["tumor_density"] >= 0.82 and row["mac_density"] <= 0.18:
        return "Tumor-dense immune-sparse"
    return "Mixed transition"


def attach_clusters(windows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    feature_values = windows[FEATURE_COLUMNS].to_numpy(dtype=float)
    scaled, mean, std = standardize(feature_values)
    labels, centroids = run_kmeans(scaled, N_CLUSTERS, SEED)
    pca_scores, components = run_pca(scaled, 2)

    windows = windows.copy()
    windows["cluster_id"] = labels
    windows["PC1"] = pca_scores[:, 0]
    windows["PC2"] = pca_scores[:, 1]

    centroids_raw = centroids * std + mean
    centroid_df = pd.DataFrame(centroids_raw, columns=FEATURE_COLUMNS)
    centroid_df["cluster_id"] = np.arange(N_CLUSTERS)
    centroid_df["cluster_label"] = centroid_df.apply(describe_cluster, axis=1)

    label_map = {}
    used = {}
    for _, row in centroid_df.iterrows():
        base = row["cluster_label"]
        used[base] = used.get(base, 0) + 1
        label = base if used[base] == 1 else f"{base} #{used[base]}"
        label_map[int(row["cluster_id"])] = label
    centroid_df["cluster_label"] = centroid_df["cluster_id"].map(label_map)
    windows["cluster_label"] = windows["cluster_id"].map(label_map)

    loading_df = pd.DataFrame(components.T, columns=["PC1_loading", "PC2_loading"])
    loading_df.insert(0, "feature", FEATURE_COLUMNS)
    return windows, centroid_df, loading_df


def save_tables(windows: pd.DataFrame, centroids: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    keep_cols = [
        "window_id", "patient_id", "sample_name", "sample_role", "met_suffix",
        "grid_y", "grid_x", "total_cells", "Tumor", "M1", "M2",
        "tumor_density", "mac_density", "m1_to_tumor", "m2_to_tumor",
        "m2_mac_ratio", "m2_outer_bias", "cluster_id", "cluster_label", "PC1", "PC2",
    ]
    windows[keep_cols].to_csv(TABLE_DIR / "window_features_clustered.tsv", sep="\t", index=False)
    centroids.to_csv(TABLE_DIR / "cluster_centroids.tsv", sep="\t", index=False)

    comp = (
        windows.groupby(["patient_id", "sample_name", "sample_role", "met_suffix", "cluster_label"])
        .size()
        .rename("n_windows")
        .reset_index()
    )
    total = comp.groupby(["patient_id", "sample_name"])["n_windows"].transform("sum")
    comp["window_fraction"] = comp["n_windows"] / total
    comp.to_csv(TABLE_DIR / "sample_cluster_composition.tsv", sep="\t", index=False)

    pair_comp = comp.pivot_table(
        index=["patient_id", "sample_role", "sample_name", "met_suffix"],
        columns="cluster_label",
        values="window_fraction",
        fill_value=0.0,
    ).reset_index()
    pair_comp.to_csv(TABLE_DIR / "sample_cluster_composition_wide.tsv", sep="\t", index=False)
    return comp, pair_comp


def plot_pca(windows: pd.DataFrame, centroids: pd.DataFrame) -> None:
    plt.figure(figsize=(8.2, 6.4))
    for cluster_id, group in windows.groupby("cluster_id"):
        label = group["cluster_label"].iloc[0]
        plt.scatter(group["PC1"], group["PC2"], s=22, alpha=0.65, label=label, color=CLUSTER_COLORS[cluster_id % len(CLUSTER_COLORS)])
    plt.axhline(0, color="#cfc4b8", lw=0.8)
    plt.axvline(0, color="#cfc4b8", lw=0.8)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("Local Window Clusters in PCA Space")
    plt.legend(frameon=False, fontsize=9)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "window_cluster_pca.png", dpi=220)
    plt.close()


def plot_centroid_heatmap(centroids: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    data = centroids.set_index("cluster_label")[FEATURE_COLUMNS]
    im = ax.imshow(data.to_numpy(), aspect="auto", cmap="RdYlBu_r")
    ax.set_xticks(np.arange(len(FEATURE_COLUMNS)))
    ax.set_xticklabels(FEATURE_COLUMNS, rotation=35, ha="right")
    ax.set_yticks(np.arange(len(data.index)))
    ax.set_yticklabels(list(data.index))
    ax.set_title("Cluster Feature Centroids")
    fig.colorbar(im, ax=ax, shrink=0.84)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "cluster_centroid_heatmap.png", dpi=220)
    plt.close()


def plot_cluster_composition(comp: pd.DataFrame, suffix: str, output_name: str, title: str) -> pd.DataFrame:
    subset = comp[comp["met_suffix"] == suffix].copy()
    if subset.empty:
        return subset
    summary = (
        subset.groupby(["sample_role", "cluster_label"])["window_fraction"]
        .mean()
        .reset_index()
    )
    labels = list(summary["cluster_label"].drop_duplicates())
    primary_vals = [summary[(summary["sample_role"] == "Primary") & (summary["cluster_label"] == lab)]["window_fraction"].mean() if not summary[(summary["sample_role"] == "Primary") & (summary["cluster_label"] == lab)].empty else 0 for lab in labels]
    met_vals = [summary[(summary["sample_role"] == "Metastasis") & (summary["cluster_label"] == lab)]["window_fraction"].mean() if not summary[(summary["sample_role"] == "Metastasis") & (summary["cluster_label"] == lab)].empty else 0 for lab in labels]

    x = np.arange(len(labels))
    width = 0.34
    plt.figure(figsize=(9.4, 5.0))
    plt.bar(x - width / 2, primary_vals, width=width, label="Primary", color="#8a7c6f")
    plt.bar(x + width / 2, met_vals, width=width, label="Metastasis", color="#305f52")
    plt.xticks(x, labels, rotation=20, ha="right")
    plt.ylabel("平均窗口占比")
    plt.title(title)
    plt.legend(frameon=False)
    plt.tight_layout()
    plt.savefig(FIG_DIR / output_name, dpi=220)
    plt.close()
    return summary


def representative_windows(windows: pd.DataFrame) -> pd.DataFrame:
    reps = []
    for cluster_id, group in windows.groupby("cluster_id"):
        center = group[FEATURE_COLUMNS].mean().to_numpy()
        values = group[FEATURE_COLUMNS].to_numpy()
        dist = np.sum((values - center) ** 2, axis=1)
        rep = group.iloc[int(np.argmin(dist))].copy()
        reps.append(rep)
    rep_df = pd.DataFrame(reps).sort_values("cluster_id")
    rep_df.to_csv(TABLE_DIR / "representative_windows.tsv", sep="\t", index=False)
    return rep_df


def plot_representative_windows(windows: pd.DataFrame, reps: pd.DataFrame) -> None:
    fig, axes = plt.subplots(len(reps), 2, figsize=(8.8, 3.0 * len(reps)))
    if len(reps) == 1:
        axes = np.array([axes])
    for row_idx, (_, rep) in enumerate(reps.iterrows()):
        sample_windows = windows[(windows["sample_name"] == rep["sample_name"])]
        rect_x = rep["grid_x"] / GRID_SIZE
        rect_y = rep["grid_y"] / GRID_SIZE
        rect_w = 1 / GRID_SIZE
        rect_h = 1 / GRID_SIZE
        for col_idx, role in enumerate(["Primary", "Metastasis"]):
            ax = axes[row_idx, col_idx]
            sample_name = rep["sample_name"]
            patient_id = rep["patient_id"]
            if role == "Metastasis":
                candidates = windows[(windows["patient_id"] == patient_id) & (windows["sample_role"] == "Metastasis")]
            else:
                candidates = windows[(windows["patient_id"] == patient_id) & (windows["sample_role"] == "Primary")]
            title_name = candidates["sample_name"].iloc[0]
            path = None
            for pair in load_pairs():
                if pair["patient_id"] != str(patient_id):
                    continue
                path = pair["primary_analysis_path"] if role == "Primary" else pair["met_analysis_path"]
                break
            pts = load_points(path)
            pts = pts.sample(min(len(pts), 3500), random_state=SEED)
            color_map = {"Tumor": "#df5a43", "M1": "#187795", "M2": "#dc9b1f"}
            alpha_map = {"Tumor": 0.12, "M1": 0.88, "M2": 0.88}
            size_map = {"Tumor": 4, "M1": 12, "M2": 12}
            for cell_type in ["Tumor", "M1", "M2"]:
                subset = pts[pts["cell_type"] == cell_type]
                ax.scatter(subset["nx"], subset["ny"], s=size_map[cell_type], c=color_map[cell_type], alpha=alpha_map[cell_type], edgecolors="none")
            ax.add_patch(plt.Rectangle((rect_x, rect_y), rect_w, rect_h, fill=False, lw=2.0, ec="#305f52"))
            ax.set_xlim(0, 1)
            ax.set_ylim(1, 0)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"{rep['cluster_label']} | {role} {title_name}", fontsize=10)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "representative_window_examples.png", dpi=220)
    plt.close()


def build_conclusion_text(comp: pd.DataFrame) -> list[str]:
    lines = []
    r_only = comp[comp["met_suffix"] == "R"].copy()
    if r_only.empty:
        return ["未找到 R-only 样本，无法输出与主结论对齐的分层结论。"]

    summary = (
        r_only.groupby(["sample_role", "cluster_label"])["window_fraction"]
        .mean()
        .unstack(fill_value=0.0)
    )
    delta = summary.loc["Metastasis"] - summary.loc["Primary"]
    ranked = delta.sort_values(ascending=False)
    lines.append("R-only 分层下，转移灶中平均占比升高最多的局部模式：")
    for label, value in ranked.head(2).items():
        lines.append(f"- {label}: 平均窗口占比变化 {value:+.3f}")
    lines.append("R-only 分层下，转移灶中平均占比下降最多的局部模式：")
    for label, value in ranked.tail(2).sort_values().items():
        lines.append(f"- {label}: 平均窗口占比变化 {value:+.3f}")

    if any("M2 outer-biased" in label for label in delta.index):
        m2_like = [label for label in delta.index if "M2 outer-biased" in label]
        for label in m2_like:
            lines.append(f"结论提示: {label} 在转移灶中的变化为 {delta[label]:+.3f}，可用于支持“M2 更外围化”的拓展解释。")
    if any("Tumor-M1 support" in label for label in delta.index):
        m1_like = [label for label in delta.index if "Tumor-M1 support" in label]
        for label in m1_like:
            lines.append(f"结论提示: {label} 在转移灶中的变化为 {delta[label]:+.3f}，可用于支持“Tumor-M1 互作下降”的拓展解释。")
    return lines


def write_summary_markdown(lines: list[str], centroids: pd.DataFrame) -> None:
    centroid_text = centroids[["cluster_label", "tumor_density", "mac_density", "m1_to_tumor", "m2_to_tumor", "m2_mac_ratio", "m2_outer_bias"]].round(3)
    header = "| cluster_label | tumor_density | mac_density | m1_to_tumor | m2_to_tumor | m2_mac_ratio | m2_outer_bias |"
    divider = "|---|---:|---:|---:|---:|---:|---:|"
    rows = [
        f"| {row['cluster_label']} | {row['tumor_density']:.3f} | {row['mac_density']:.3f} | {row['m1_to_tumor']:.3f} | {row['m2_to_tumor']:.3f} | {row['m2_mac_ratio']:.3f} | {row['m2_outer_bias']:.3f} |"
        for _, row in centroid_text.iterrows()
    ]
    md_lines = [
        "# 局部窗口聚类拓展结论摘要",
        "",
        "## 终端结论",
        "",
    ]
    md_lines.extend([f"- {line}" for line in lines])
    md_lines.extend([
        "",
        "## 聚类模式中心",
        "",
        header,
        divider,
        *rows,
        "",
        "## 解读建议",
        "",
        "- `M2 outer-biased` 可用于补充支持“转移灶更偏 M2 型构成，且更表现为外围化”。",
        "- 若后续继续拓展，可在此基础上增加窗口级 UMAP、窗口示例截图和模式比例统计图。",
    ])
    (OUTPUT_DIR / "拓展部分结论摘要.md").write_text("\n".join(md_lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    windows = build_window_table()
    windows, centroids, loadings = attach_clusters(windows)
    comp, comp_wide = save_tables(windows, centroids)
    loadings.to_csv(TABLE_DIR / "pca_feature_loadings.tsv", sep="\t", index=False)
    reps = representative_windows(windows)

    plot_pca(windows, centroids)
    plot_centroid_heatmap(centroids)
    plot_cluster_composition(comp, "R", "r_only_cluster_composition.png", "R-only: local pattern fractions in Primary vs Metastasis")
    plot_cluster_composition(comp, "L", "l_only_cluster_composition.png", "L-only: local pattern fractions in Primary vs Metastasis")
    plot_representative_windows(windows, reps)

    conclusion_lines = build_conclusion_text(comp)
    write_summary_markdown(conclusion_lines, centroids)

    print("局部窗口聚类拓展分析已完成。")
    print(f"窗口特征表: {TABLE_DIR / 'window_features_clustered.tsv'}")
    print(f"聚类中心表: {TABLE_DIR / 'cluster_centroids.tsv'}")
    print(f"代表性图片目录: {FIG_DIR}")
    print()
    print("终端结论摘要:")
    for line in conclusion_lines:
        print(line)


if __name__ == "__main__":
    main()
