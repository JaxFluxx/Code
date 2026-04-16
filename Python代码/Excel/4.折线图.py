from openpyxl import Workbook,load_workbook
from openpyxl.chart import LineChart, Reference

wb = load_workbook(r'C:\Users\何嘉\Desktop\test.xlsx')
#ws = wb.active
ws = wb['Sheet4']
print(ws.title)

# 准备数据
rows = [
    ['月份', '桃子', '西瓜', '龙眼'],
    [1, 38, 28, 29],
    [2, 52, 21, 35],
    [3, 39, 20, 69],
    [4, 51, 29, 41],
    [5, 29, 39, 31],
    [6, 30, 41, 39],
]
for row in rows:
    ws.append(row)

# 创建图表
c1 = LineChart()    # 创建折线图
c1.title = "折线图"  # 标题
c1.style = 13  # 样式
c1.y_axis.title = '销量'  # Y轴
c1.x_axis.title = '月份'  # X轴

# 选择数据范围
data = Reference(ws, min_col=2, min_row=1, max_col=4, max_row=7)    # 选择A2:D7
c1.add_data(data, titles_from_data=True)    # 添加数据

# 线条样式
s0 = c1.series[0]   # 选择第一个系列
s0.marker.symbol = "triangle"  # triangle为三角形标记， 可选circle、dash、diamond、dot、picture、plus、square、star、triangle、x、auto
s0.marker.graphicalProperties.solidFill = "FF0000"  # 填充颜色
s0.marker.graphicalProperties.line.solidFill = "0000FF"  # 边框颜色
# s0.graphicalProperties.line.noFill = True  # 改为True则隐藏线条，但显示标记形状

s1 = c1.series[1]   # 选择第二个系列
s1.graphicalProperties.line.solidFill = "00AAAA"
s1.graphicalProperties.line.dashStyle = "sysDot"  # 线条点状样式
s1.graphicalProperties.line.width = 80000  # 线条大小，最大20116800EMUs

s2 = c1.series[2]  # 采用默认设置
s2.smooth = True  # 线条平滑

ws.add_chart(c1, "A8")  # 图表位置

wb.save(r'C:\Users\何嘉\Desktop\test.xlsx')    # 保存文件

