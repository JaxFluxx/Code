# 原始数据重分析与显著性检验思路

## 目标

基于原始目录：

`/Users/jia/Desktop/学习 /毕业设计/实验/CODEX全部分析数据-20260116`

重新读取 `objects.tsv`，按 baseline 原定义重建 `Tumor / M1 / M2` 三类细胞，并探索在不引入新细胞类型前，哪些维度更可能支持稳定结论。

## 保持一致的 baseline 口径

- `Tumor = PanCK+ & CD68-`
- `M1 = CD68+ & CD86+ & CD163- & PanCK-`
- `M2 = CD68+ & CD163+ & CD86- & PanCK-`
- `Ambiguous Mac = CD68+ & CD86+ & CD163+ & PanCK-`

说明：

- 当前这套规则是“严格规则分类”。
- 如果后续面向论文表述，更建议写成 `M1-like / M2-like`，因为它们只是基于 marker 组合定义出来的代理群体，不等价于体内真实的完整功能状态。

## 为什么这次先不扩细胞类型

当前优先任务不是立刻扩展分类，而是先判断：

1. baseline 三类细胞的哪些维度仍然可用
2. 哪些结论只是“图上趋势”
3. 哪些维度在配对检验后更稳

## 本次重点探索的维度

### 1) 数量与比例

- `tumor_n`
- `m1_n`
- `m2_n`
- `mac_n = m1_n + m2_n`
- `m1_to_tumor = m1_n / tumor_n`
- `m2_to_tumor = m2_n / tumor_n`
- `mac_to_tumor = mac_n / tumor_n`
- `m1_frac_of_mac = m1_n / (m1_n + m2_n)`
- `m2_frac_of_mac = m2_n / (m1_n + m2_n)`

选择原因：

- `M2 / (M1 + M2)` 受低 `M1` 影响大
- `*_to_tumor` 的分母更稳定，通常比 `M2/(M1+M2)` 更适合做 paired 结论

### 2) 空间接近程度

- `within_20_M1`
- `within_20_M2`
- `within_30_M1`
- `within_30_M2`

定义：

- 某类细胞到最近 `Tumor` 的距离不超过阈值的比例

阈值说明：

- 保留 baseline 已使用的 `20` 与 `30`
- 这样可以直接和原结论对齐
- 暂不额外引入新半径，避免结果口径混乱

### 3) 邻域互作强度

- `enrich_20_Tumor_M1`
- `enrich_30_Tumor_M1`
- `enrich_20_Tumor_M2`
- `enrich_30_Tumor_M2`

定义：

- 以每个 `Tumor` 为中心，统计半径内目标细胞数，再对所有 `Tumor` 取平均

### 4) 距离分布

- `m1_dist_median`
- `m2_dist_median`
- `dist_gap_m2_minus_m1 = m2_dist_median - m1_dist_median`

选择原因：

- 比 `within_20/30` 少一些阈值依赖
- 更适合讨论“更外围化”这类连续趋势

## 显著性检验策略

### 主检验

- 使用 paired Wilcoxon signed-rank test
- 分组：
  - `R`
  - `L`
  - `QT`
  - `ALL`

### 低 M1 稳健性分析

增加一个过滤版本：

- `min_m1_both_50`

含义：

- 仅保留原发灶和转移灶中 `M1_n >= 50` 的配对

阈值选择理由：

- 不是生物学金标准
- 是一个用于去掉极低计数样本的工程阈值
- 比 `10/20` 更严格，能更明显识别“低 M1 导致比例不稳”的问题

后续如有需要，可再测试：

- `M1_n >= 30`
- `M1_n >= 100`

## 绘图策略

### 图 1：M1 趋势指标

按组展示配对折线图：

- `m1_to_tumor`
- `enrich_20_Tumor_M1`
- `enrich_30_Tumor_M1`

原因：

- 这是最贴近“Tumor-M1 互作下降”的三组指标

### 图 2：M2 空间位置指标

按组展示配对折线图：

- `m2_dist_median`
- `within_20_M2`
- `within_30_M2`

原因：

- 这是最贴近“M2 更外围化”的连续距离 + 阈值邻域双重描述

### 图 3：显著性热图

展示：

- 行：组别与过滤策略
- 列：关键指标
- 格子内容：`p` 值

原因：

- 便于一眼看出到底哪些结果只是趋势，哪些更接近稳定信号

## 输出

输出目录：

`/Users/jia/Desktop/学习 /毕业设计/实验/CODEX_raw_reanalysis_significance`

主要文件：

- `sample_summary.tsv`
- `pair_manifest.tsv`
- `pair_metrics.tsv`
- `paired_significance.tsv`
- `M1趋势指标_分组配对折线图.png`
- `M2空间指标_分组配对折线图.png`
- `显著性热图.png`
- `R组_低M1过滤后_M1趋势指标.png`
