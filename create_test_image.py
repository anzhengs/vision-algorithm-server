import cv2
import numpy as np

# 创建黑色背景（尺寸：高400px，宽600px，3通道彩色）
img = np.zeros((400, 600, 3), dtype=np.uint8)

# 画白色圆形（圆心(150,200)，半径50px，填充）
cv2.circle(img, (150, 200), 50, (255, 255, 255), -1)

# 画白色矩形（左上角(250,150)，右下角(350,250)，填充）
cv2.rectangle(img, (250, 150), (350, 250), (255, 255, 255), -1)

# 画白色三角形（顶点坐标(450,150)、(400,250)、(500,250)，填充）
pts = np.array([[450, 150], [400, 250], [500, 250]], np.int32)
cv2.fillPoly(img, [pts], (255, 255, 255))

# 保存图片到当前目录（文件名：gem_test.png）
cv2.imwrite('gem_test.png', img)
print("测试图片已创建: gem_test.png")
