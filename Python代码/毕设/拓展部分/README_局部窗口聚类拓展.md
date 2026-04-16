# 局部窗口聚类拓展说明

## 放置位置

- 代码目录：`/Users/jia/Desktop/学习 /Code/Python代码/毕设/拓展部分`
- 输出目录：`/Users/jia/Desktop/学习 /毕业设计/实验/拓展部分_局部窗口聚类`

## 这个拓展在做什么

主分析已经完成样本级空间指标比较，这个拓展进一步把每个样本切成很多局部窗口，再对窗口做无监督聚类，目的是回答：

- 原发灶和转移灶分别更常出现哪些局部微环境模式？
- 哪类局部模式能支持 `Tumor-M1 互作下降`？
- 哪类局部模式能支持 `M2 占比升高`？
- 哪类局部模式能支持 `M2 更外围化`？

## 简要流程

1. 读取 `pair_manifest.tsv` 和每个样本的 `*_analysis_cells.tsv`
2. 将每个样本按归一化坐标切成 `6 x 6` 局部窗口
3. 为每个窗口计算：
   - `tumor_density`
   - `mac_density`
   - `m1_to_tumor`
   - `m2_to_tumor`
   - `m2_mac_ratio`
   - `m2_outer_bias`
   - `m1_minus_m2`
4. 对窗口特征标准化
5. 使用轻量 KMeans 聚类
6. 用聚类中心给每类窗口贴解释性标签
7. 输出图表和必要表格

## 主要输出

### 表格

- `tables/window_features_clustered.tsv`
  每个局部窗口的特征和聚类结果

- `tables/cluster_centroids.tsv`
  每个聚类中心的特征均值，可用于解释每一类模式

- `tables/sample_cluster_composition.tsv`
  每个样本里各类窗口模式所占比例

- `tables/representative_windows.tsv`
  每个聚类最具代表性的窗口

### 图片

- `figures/window_cluster_pca.png`
  所有局部窗口在 PCA 二维空间中的分布

- `figures/cluster_centroid_heatmap.png`
  各聚类模式的特征热图

- `figures/r_only_cluster_composition.png`
  R-only 下原发灶 vs 转移灶的模式占比对比

- `figures/representative_window_examples.png`
  各聚类的代表性窗口示意图

## 如何运行

```bash
cd '/Users/jia/Desktop/学习 /Code/Python代码/毕设/拓展部分'
python3 local_window_cluster_analysis.py
```

## 结果怎么解释

最理想的解释方式不是“模型把样本分开了”，而是：

- 机器总结出了几类局部微环境模式
- 原发灶和转移灶在这些模式的构成上不同
- 这种模式差异能补充支持主分析中的三条结论

## 推荐写法

可以在论文拓展部分写成：

“在主分析完成配对比较的基础上，本文进一步采用基于局部空间窗口的无监督聚类方法，对 Tumor/M1/M2 三类细胞构成及其局部关系进行模式归纳。结果显示，原发灶与转移灶在局部空间模式组成上存在系统差异，其中转移灶更易出现 M2 偏高且更外围化的窗口模式，而原发灶保留更多具有 Tumor-M1 支持特征的局部模式。这与主分析中观察到的 Tumor-M1 互作下降、M2 构成升高及 M2 外围化趋势相一致。” 
