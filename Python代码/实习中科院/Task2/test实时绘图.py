#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import pandas as pd
import matplotlib
matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtCore import QTimer

DEFAULT_FILE = r"/Users/jia/Desktop/学习 /Python代码/实习中科 院/Task2/system_log.csv"
# 也可用命令行传入路径：python app.py "/path/to/system_log.csv"


plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

class RealtimeACC(QWidget):
    def __init__(self, csv_path: str):
        super().__init__()
        # 修正路径里可能写成了 "\ " 的情况
        self.csv_path = csv_path.replace("\\ ", " ")
        self.last_mtime = None
        self.df = None

        self.init_ui()
        self.start_timer()

    def init_ui(self):
        self.resize(1000, 520)
        self.setWindowTitle("ACC 实时折线图（x: time, y: ACC）")

        # 中文显示
        plt.rcParams["font.sans-serif"] = ["SimHei"]
        plt.rcParams["axes.unicode_minus"] = False

        # 画布
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # 初始画布样式
        self.ax.set_xlabel("time (s)")
        self.ax.set_ylabel("ACC (TFLOPS)")
        self.ax.grid(True, linestyle="--", alpha=0.3)

    def start_timer(self):
        self.timer = QTimer(self)
        # 每 500 ms 检查一次文件是否更新
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(500)

    def file_changed(self) -> bool:
        """文件是否有更新（按修改时间判断）"""
        try:
            mtime = os.path.getmtime(self.csv_path)
        except FileNotFoundError:
            return False
        if self.last_mtime is None or mtime != self.last_mtime:
            self.last_mtime = mtime
            return True
        return False

    def read_csv(self):
        """读取 CSV，自动识别分隔符；兼容 UTF-8/BOM。"""
        if not os.path.exists(self.csv_path):
            return None

        # sep=None + engine='python' 让 pandas 自动猜分隔符（逗号/制表符都可）
        try:
            df = pd.read_csv(self.csv_path, sep=None, engine="python", encoding="utf-8-sig")
        except Exception:
            # 兜底再试一次默认逗号
            df = pd.read_csv(self.csv_path, encoding="utf-8-sig")

        # 统一列名（去空白）
        df.columns = [c.strip() for c in df.columns]

        # 可能叫 ACC_TFLOPS 或 ACC，择其一
        acc_col = None
        for cand in ["ACC_TFLOPS", "ACC"]:
            if cand in df.columns:
                acc_col = cand
                break
        if acc_col is None:
            raise ValueError("CSV 里找不到 ACC/ACC_TFLOPS 列")

        if "time" not in df.columns:
            raise ValueError("CSV 里找不到 time 列")

        # 转数值，丢弃无法解析的行
        df["time"] = pd.to_numeric(df["time"], errors="coerce")
        df[acc_col] = pd.to_numeric(df[acc_col], errors="coerce")
        df = df.dropna(subset=["time", acc_col])

        # 按时间排序
        df = df.sort_values("time")
        df = df.reset_index(drop=True)

        return df, acc_col

    def update_plot(self):
        if not self.file_changed() and self.df is not None:
            # 文件未变化就不重绘
            return

        try:
            result = self.read_csv()
            if result is None:
                return
            df, acc_col = result
        except Exception as e:
            # 读文件失败时，不要频繁弹错；仅打印一次或间隔打印
            # 这里简单略过
            return

        self.df = df

        # 清空并重画
        self.ax.cla()
        self.ax.set_xlabel("time (s)")
        self.ax.set_ylabel("ACC (TFLOPS)")
        self.ax.grid(True, linestyle="--", alpha=0.3)

        x = df["time"].values
        y = df[acc_col].values

        self.ax.plot(x, y, linewidth=1.8, marker="o", markersize=4)
        # 可选：只显示最近 N 个点，比如 200 个
        # N = 200
        # if len(x) > N:
        #     self.ax.set_xlim(x[-N], x[-1])

        # 自适应边界留白
        if len(y) > 0:
            ymin, ymax = float(y.min()), float(y.max())
            if ymin == ymax:
                ymin -= 0.5
                ymax += 0.5
            self.ax.set_ylim(ymin - 0.05 * abs(ymax - ymin), ymax + 0.05 * abs(ymax - ymin))

        self.ax.set_title(f"实时 ACC 曲线（点数：{len(x)}）")
        self.canvas.draw()

def main():
    csv_path = DEFAULT_FILE
    # 支持命令行覆盖路径
    if len(sys.argv) > 1:
        # 如果把路径写成了 “\ ”，也自动修正
        csv_path = " ".join(sys.argv[1:]).replace("\\ ", " ")
    app = QApplication(sys.argv)
    w = RealtimeACC(csv_path)
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
