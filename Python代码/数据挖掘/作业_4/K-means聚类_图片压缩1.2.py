# 读取图片：使用io.imread读取名为china.jpg的图片，并将其转换为一个包含RGB值的二维数组。
# MiniBatchKMeans模型：定义小批量KMeans模型，设置聚类中心数量为16，并对数据进行训练。
# 颜色替换：通过聚类标签将每个像素的颜色替换为对应的聚类中心颜色。
# 重新整形：将压缩后的颜色数组重新整形成原始图片的形状，以便显示。
# 显示颜色空间：使用plot_pixels函数展示压缩后的颜色空间。
# 展示原始和压缩后的图片：使用imshow函数展示原始图片和经过16种颜色压缩后的图片。
# 压缩为8种颜色：重复前面的步骤，将聚类中心数量改为8，并显示相应的结果。



import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import MiniBatchKMeans
from skimage import io
from sklearn.datasets import load_sample_image

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] #苹果系统显示中文字体

# 读取图片
china_image = load_sample_image("china.jpg")  # 使用内置样本图片
# 将图片数据从0-255的整数范围转换为0-1的浮点数范围，便于处理
image_data = china_image / 255.0
# 将图片数据重塑为二维数组，其中每一行代表一个像素，三个值分别是RGB颜色通道的值
image_data_reshaped = image_data.reshape(-1, 3)

# 1）使用 MiniBatchKMeans 进行颜色压缩为16种颜色
kmeans_16_colors = MiniBatchKMeans(n_clusters=16, random_state=0)  # 定义小批量KMeans模型，设置聚类中心为16
kmeans_16_colors.fit(image_data_reshaped)  # 对图片数据进行聚类

# 使用聚类标签将每个像素的颜色替换为对应的聚类中心颜色
compressed_colors_16 = kmeans_16_colors.cluster_centers_[kmeans_16_colors.predict(image_data_reshaped)]
# 将新的颜色数组重新整形成原始图片的形状
china_recolored_16 = compressed_colors_16.reshape(china_image.shape)

# 2）显示原始图片和16种颜色压缩后的图片
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)  # 1行2列，第1个位置
plt.imshow(china_image)  # 显示原始图片
plt.title("原始图片")  # 设置标题为中文
plt.axis('off')  # 关闭坐标轴

plt.subplot(1, 2, 2)  # 1行2列，第2个位置
plt.imshow(china_recolored_16)  # 显示压缩后的图片
plt.title("16种颜色图片")  # 设置标题为中文
plt.axis('off')  # 关闭坐标轴

plt.show()

# 复用前面的代码，压缩为8种颜色
kmeans_8_colors = MiniBatchKMeans(n_clusters=8, random_state=0)  # 定义小批量KMeans模型，设置聚类中心为8
kmeans_8_colors.fit(image_data_reshaped)  # 对图片数据进行聚类

# 使用8种颜色替换像素的颜色
compressed_colors_8 = kmeans_8_colors.cluster_centers_[kmeans_8_colors.predict(image_data_reshaped)]
# 将新的颜色数组重新整形成原始图片的形状
china_recolored_8 = compressed_colors_8.reshape(china_image.shape)

# 展示压缩后的颜色空间（8种颜色）
def display_color_space(data, colors, title):
    """展示颜色空间的函数"""
    plt.figure(figsize=(8, 6))
    plt.imshow(colors.reshape(1, -1, 3))  # 将颜色reshape为一行多列的格式
    plt.title(title)  # 设置标题为中文
    plt.axis('off')  # 关闭坐标轴
    plt.show()

# 展示压缩后的颜色空间（8种颜色）
display_color_space(image_data_reshaped, colors=kmeans_8_colors.cluster_centers_, title="压缩后的颜色空间：8种颜色")

# 展示原始图片与压缩后的8种颜色的图片
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)  # 1行2列，第1个位置
plt.imshow(china_image)  # 显示原始图片
plt.title("原始图片")  # 设置标题为中文
plt.axis('off')  # 关闭坐标轴

plt.subplot(1, 2, 2)  # 1行2列，第2个位置
plt.imshow(china_recolored_8)  # 显示压缩后的8种颜色的图片
plt.title("8种颜色图片")  # 设置标题为中文
plt.axis('off')  # 关闭坐标轴

plt.show()
