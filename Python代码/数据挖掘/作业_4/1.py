import matplotlib.pyplot as plt

# 定义裁剪窗口的边界
x_min, y_min = 0, 0  # 左下角
x_max, y_max = 10, 10  # 右上角

# 定义端点的区域码计算
INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

def compute_code(x, y):
    code = INSIDE
    if x < x_min:
        code |= LEFT
    elif x > x_max:
        code |= RIGHT
    if y < y_min:
        code |= BOTTOM
    elif y > y_max:
        code |= TOP
    return code

# 实现Cohen-Sutherland裁剪算法
def cohen_sutherland_clip(x1, y1, x2, y2):
    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)
    while True:
        if code1 == 0 and code2 == 0:
            return (x1, y1, x2, y2)  # 完全在窗口内
        elif code1 & code2 != 0:
            return None  # 完全在窗口外
        else:
            code_out = code1 if code1 != 0 else code2
            if code_out & TOP:
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1)
                y = y_max
            elif code_out & BOTTOM:
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1)
                y = y_min
            elif code_out & RIGHT:
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x = x_max
            elif code_out & LEFT:
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x = x_min
            if code_out == code1:
                x1, y1 = x, y
                code1 = compute_code(x1, y1)
            else:
                x2, y2 = x, y
                code2 = compute_code(x2, y2)

# 示例数据：原始线段
lines = [(-5, 5, 15, 5), (5, -5, 5, 15), (-5, -5, 15, 15)]
clipped_lines = []

# 裁剪线段
for line in lines:
    result = cohen_sutherland_clip(*line)
    if result:
        clipped_lines.append(result)

# 绘制结果
plt.figure(figsize=(8, 8))
plt.plot([x_min, x_max, x_max, x_min, x_min], [y_min, y_min, y_max, y_max, y_min], 'r-', label="裁剪窗口")
for line in lines:
    plt.plot([line[0], line[2]], [line[1], line[3]], 'g--', label="原始线段")
# 绘制裁剪后的线段
for clipped_line in clipped_lines:
    plt.plot([clipped_line[0], clipped_line[2]], [clipped_line[1], clipped_line[3]], 'b-', label="裁剪后线段")

# 调整图例和图形显示
plt.title("线段裁剪示例 (Cohen-Sutherland算法)")
plt.xlabel("X坐标")
plt.ylabel("Y坐标")
plt.legend(loc="upper right")
plt.grid()
plt.show()