import numpy as np

# 相机内参
fx, fy, cx, cy = 957.01226348, 934.81781967, 982.79102164, 499.9173914
camera_intrinsics = np.array(
    [[fx, 0, cx],
     [0, fy, cy],
     [0, 0, 1]], dtype=np.float32
)

# 相机坐标系下的点
camera_point = np.array([-0.45332766, -0.29803706, 1.51791097])

# 将相机点转化为列向量
camera_point = camera_point.reshape(3, 1)

# 计算投影点
pixel_point = np.dot(camera_intrinsics, camera_point)

# 检查是否需要归一化
if pixel_point[2, 0] == 0:
    raise ValueError("归一化因子为0，无法进行归一化计算。请检查输入数据。")

# 归一化像素坐标
pixel_x = pixel_point[0, 0] / pixel_point[2, 0]
pixel_y = pixel_point[1, 0] / pixel_point[2, 0]

# 打印结果
print("Pixel coordinates (x, y): ({:.2f}, {:.2f})".format(pixel_x, pixel_y))

# # 其他矩阵操作
# A = np.array([[1, 2], [3, 4]])
# B = np.array([[5, 6], [7, 8]])

# # 矩阵加法
# C = A + B

# # 矩阵乘法
# D = np.dot(A, B)

# # 矩阵转置
# E = np.transpose(A)

# print("矩阵加法结果:\n", C)
# print("矩阵乘法结果:\n", D)
# print("矩阵转置结果:\n", E)
