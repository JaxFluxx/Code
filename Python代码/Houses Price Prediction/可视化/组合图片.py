from PIL import Image
from matplotlib import pyplot as plt

# 读取四张图片的路径（注意处理路径中的空格和特殊字符）
img_paths = [
    "/Users/jia/Desktop/论文/可视化/Random Forest_价格对比图折线1.png",
    "/Users/jia/Desktop/论文/可视化/XGBoost对比折线图1.png",
    "/Users/jia/Desktop/论文/可视化/LightGBM_折线对比图1.png",
    "/Users/jia/Desktop/论文/可视化/Ensemble model_对比折线图1.png"
]

# 打开图像
imgs = [Image.open(p) for p in img_paths]

# 确保所有图像大小一致（这里以第一张为标准）
width, height = imgs[0].size
imgs = [img.resize((width, height)) for img in imgs]

# 创建一张新图像，大小为2x2组合
new_img = Image.new('RGB', (width * 2, height * 2))

# 粘贴图像到新图像中
new_img.paste(imgs[0], (0, 0))                 # 左上
new_img.paste(imgs[1], (width, 0))             # 右上
new_img.paste(imgs[2], (0, height))            # 左下
new_img.paste(imgs[3], (width, height))        # 右下

# 保存新图像
output_path = "/Users/jia/Desktop/学习 /科研/独立论文部分/图片/组合图2x2.png"
new_img.save(output_path)
new_img.show()

print(f"✅ 图片已保存至：{output_path}")
