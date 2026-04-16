import numpy as np          # 引入NumPy库，用于处理数组和矩阵运算
import random               # 引入random库，用于生成随机数和随机操作
import math                 # 引入math库，用于数学函数（如指数运算）

# ============================
# 模拟退火算法解决TSP问题
# ============================

# ----------- 1. 问题定义（距离矩阵）-------------
# 创建一个6个城市的距离矩阵（城市编号为0~5），用np.inf表示不可达
distance_matrix = np.array([
    [0, 10, 15, np.inf, 20, 30],         # 城市0到其他城市的距离
    [10, 0, 35, 25, np.inf, np.inf],     # 城市1到其他城市的距离
    [15, 35, 0, 30, 20, np.inf],         # 城市2到其他城市的距离
    [np.inf, 25, 30, 0, 15, 10],         # 城市3到其他城市的距离
    [20, np.inf, 20, 15, 0, 25],         # 城市4到其他城市的距离
    [30, np.inf, np.inf, 10, 25, 0]      # 城市5到其他城市的距离
])

# 获取城市总数（即矩阵的行/列数）
num_cities = distance_matrix.shape[0]


# ---------- 2. 路径总距离计算函数 -------------
def calculate_total_distance(route, matrix):
    """
    计算给定路径的总距离。
    如果路径中任意一段不可达（为np.inf），则返回np.inf表示非法路径。
    """
    total_dist = 0  # 初始化总距离为0
    for i in range(len(route) - 1):  # 遍历路径中的每一对相邻城市
        d = matrix[route[i]][route[i + 1]]  # 获取两城市之间的距离
        if d == np.inf:  # 如果这段路径不可达
            return np.inf  # 返回inf，代表非法解
        total_dist += d  # 累加这段路径的距离
    # 加上从终点返回起点的距离（形成闭环）
    d_back = matrix[route[-1]][route[0]]
    if d_back == np.inf:
        return np.inf
    total_dist += d_back  # 加入回到起点的距离
    return total_dist  # 返回总路径长度


# ---------- 3. 生成邻域解 -------------
def generate_neighbor(route):
    """
    生成当前路径的一个邻域解：随机交换两个城市的位置。
    """
    a, b = random.sample(range(len(route)), 2)  # 从城市编号中随机选两个不同城市
    neighbor = route.copy()  # 拷贝当前路径
    neighbor[a], neighbor[b] = neighbor[b], neighbor[a]  # 交换这两个城市的位置
    return neighbor  # 返回新的路径


# ---------- 4. 模拟退火算法主函数 -------------
def simulated_annealing(matrix, initial_temp=1000, cooling_rate=0.995, stopping_temp=1e-3, max_iter=100000):
    """
    使用模拟退火算法求解TSP问题
    参数说明：
        matrix: 城市距离矩阵
        initial_temp: 初始温度
        cooling_rate: 降温率（每次迭代温度乘以该值）
        stopping_temp: 停止迭代的最低温度
        max_iter: 最大迭代次数
    返回：
        最优路径及其对应的总距离
    """
    current_solution = list(range(num_cities))  # 初始路径为[0,1,2,...]
    current_distance = calculate_total_distance(current_solution, matrix)  # 当前路径的总距离

    best_solution = current_solution[:]  # 初始化最优解为当前解的副本
    best_distance = current_distance     # 初始化最优距离为当前距离

    temperature = initial_temp  # 设置初始温度
    iteration = 0  # 初始化迭代计数器

    # 主迭代循环
    while temperature > stopping_temp and iteration < max_iter:
        new_solution = generate_neighbor(current_solution)  # 生成一个邻域解（路径变动）
        new_distance = calculate_total_distance(new_solution, matrix)  # 计算新路径距离

        if new_distance < np.inf:  # 如果是合法路径
            delta = new_distance - current_distance  # 计算距离差值（能量变化）

            # 接受准则：如果更好就接受；如果更差则以概率接受（有利于跳出局部最优）
            if delta < 0 or random.uniform(0, 1) < math.exp(-delta / temperature):
                current_solution = new_solution  # 接受新解
                current_distance = new_distance  # 更新当前距离

                # 如果新解优于历史最优解，则更新最优解
                if new_distance < best_distance:
                    best_solution = new_solution
                    best_distance = new_distance

        temperature *= cooling_rate  # 降温
        iteration += 1  # 迭代次数+1

    return best_solution, best_distance  # 返回最优解


# ---------- 5. 程序执行与结果输出 -------------
if __name__ == "__main__":
    best_path, best_cost = simulated_annealing(distance_matrix)  # 执行模拟退火算法

    print("最优路径（城市编号顺序）：", best_path)  # 输出最优路径
    print("路径回到起点后完整路径：", best_path + [best_path[0]])  # 加上回起点
    print("总路径长度：", round(best_cost, 2))  # 输出总路径长度，保留2位小数
