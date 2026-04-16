# 例  有一线段AB，A的坐标为(1，1)，B的坐标为(4.5，4.5)，如图2-13所示。求AB的长度，以及黄金分隔点C的坐标。黄金分割点在线段的0.618处。

import math

# 定义A和B的坐标
A = (1, 1)
B = (4.5, 4.5)

# 计算线段AB的长度
length_AB = math.sqrt((B[0] - A[0])**2 + (B[1] - A[1])**2)
print(f"线段AB的长度为: {length_AB}")

# 黄金分割点的比例
golden_ratio = 0.618

# 计算黄金分割点C的坐标
C_x = A[0] + (B[0] - A[0]) * golden_ratio
C_y = A[1] + (B[1] - A[1]) * golden_ratio
print(f"黄金分割点C的坐标为: ({C_x}, {C_y})")
