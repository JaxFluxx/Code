from PIL import Image, ImageDraw, ImageFont

# 1. 打开原始图片
img = Image.open(r"/Users/jia/Desktop/学习 /科研/独立论文部分/图片/组合模型总对比图.png")   # 你的原始文件名
draw = ImageDraw.Draw(img)

# 2. 加载字体（Mac 常见中文字体）
font_title = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", 32)  # 标题用大字体
font_axis  = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", 22)  # 坐标轴用中字体
font_legend= ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", 20)  # 图例用小字体

# 3. 用白色矩形覆盖英文文字
# 参数：左上角 (x1,y1)，右下角 (x2,y2)
draw.rectangle((250, 10, 750, 50), fill="white")      # 标题区域
draw.rectangle((400, 410, 600, 440), fill="white")    # 横轴标签
draw.rectangle((10, 200, 60, 250), fill="white")      # 纵轴标签
draw.rectangle((650, 70, 1100, 130), fill="white")    # 图例区域

# 4. 在对应区域写中文文字
draw.text((260, 15), "集成模型预测 vs 实际价格", font=font_title, fill="black")
draw.text((450, 415), "样本索引", font=font_axis, fill="black")
draw.text((20, 220), "价格（万元）", font=font_axis, fill="black")
draw.text((660, 80), "实际价格（抽样）", font=font_legend, fill="black")
draw.text((660, 105), "加权集成预测（抽样）", font=font_legend, fill="black")

# 5. 保存新图片
img.save("修改后.png")
print("✅ 已生成修改后的中文图：修改后.png")
