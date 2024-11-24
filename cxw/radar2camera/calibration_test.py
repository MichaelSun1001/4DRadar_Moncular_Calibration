# import numpy as np
# import cv2
# import pandas as pd


# def load_radar_points(file_path):
#     """
#     Load radar points from CSV file.

#     Parameters:
#     file_path (str): Path to the CSV file

#     Returns:
#     np.array: Radar point cloud data
#     """
#     radar_data = pd.read_csv(file_path)
#     radar_points = radar_data[['Rep_X', 'Rep_Y',
#                                'Rep_Z']].values.astype(np.float32)
#     return radar_points


# def load_camera_points(file_path):
#     """
#     Load camera points from CSV file.

#     Parameters:
#     file_path (str): Path to the CSV file

#     Returns:
#     np.array: Pixel points in the camera image
#     """
#     camera_data = pd.read_csv(file_path)
#     camera_points = camera_data[['X', 'Y']].values.astype(np.float32)
#     return camera_points


# def main():
#     # 设置文件路径
#     radar_file_path = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\pointcloud\csv\representative_points.csv'
#     camera_file_path = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\image\csv\camera_incenter.csv'

#     # 加载数据
#     radar_points = load_radar_points(radar_file_path)
#     camera_points = load_camera_points(camera_file_path)

#     # 检查点对数量是否匹配
#     if radar_points.shape[0] != camera_points.shape[0]:
#         raise ValueError(
#             "Number of radar points and camera points must be the same")

#     # 相机内参矩阵
#     fx, fy, cx, cy = 957.01226348, 934.81781967, 982.79102164, 499.9173914
#     camera_matrix = np.array([
#         [fx, 0, cx],
#         [0, fy, cy],
#         [0, 0, 1]
#     ], dtype=np.float32)

#     # 无畸变系数
#     dist_coeffs = np.zeros((4, 1), dtype=np.float32)

#     # 计算外参矩阵 [R | t]
#     retval, rvec, tvec = cv2.solvePnP(
#         radar_points, camera_points, camera_matrix, dist_coeffs)

#     # 检查 solvePnP 是否成功
#     if not retval:
#         raise RuntimeError("cv2.solvePnP failed")

#     # 计算旋转矩阵
#     R, _ = cv2.Rodrigues(rvec)

#     # 外参矩阵 [R | t]
#     extrinsic_matrix = np.hstack((R, tvec))

#     # 打印结果
#     print("旋转矩阵 R:\n", R)
#     print("平移向量 t:\n", tvec)
#     print("外参矩阵 [R | t]:\n", extrinsic_matrix)


# if __name__ == '__main__':
#     main()

import numpy as np
import cv2
import pandas as pd


def load_radar_points(file_path):
    """
    Load radar points from CSV file.

    Parameters:
    file_path (str): Path to the CSV file

    Returns:
    np.array: Radar point cloud data
    """
    radar_data = pd.read_csv(file_path)
    radar_points = radar_data[['Rep_X', 'Rep_Y',
                               'Rep_Z']].values.astype(np.float32)
    return radar_points


def load_camera_points(file_path):
    """
    Load camera points from CSV file.

    Parameters:
    file_path (str): Path to the CSV file

    Returns:
    np.array: Pixel points in the camera image
    """
    camera_data = pd.read_csv(file_path)
    camera_points = camera_data[['X', 'Y']].values.astype(np.float32)
    return camera_points


def main():
    # 设置文件路径
    radar_file_path = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\pointcloud\csv\representative_points.csv'
    camera_file_path = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\image\csv\camera_incenter.csv'

    # 加载数据
    radar_points = load_radar_points(radar_file_path)
    camera_points = load_camera_points(camera_file_path)

    # 相机内参矩阵
    fx, fy, cx, cy = 957.01226348, 934.81781967, 982.79102164, 499.9173914
    camera_matrix = np.array([
        [fx, 0, cx],
        [0, fy, cy],
        [0, 0, 1]
    ], dtype=np.float32)

    # 畸变系数，假设为零
    dist_coeffs = np.zeros((4, 1), dtype=np.float32)

    # 使用 RANSAC 求解外参
    retval, rvec, tvec, inliers = cv2.solvePnPRansac(
        radar_points, camera_points, camera_matrix, dist_coeffs,
        iterationsCount=100, reprojectionError=8.0, flags=cv2.SOLVEPNP_ITERATIVE
    )

    # 计算旋转矩阵
    R, _ = cv2.Rodrigues(rvec)

    # 外参矩阵 [R | t]
    extrinsic_matrix = np.hstack((R, tvec))

    # 打印结果
    print("旋转矩阵 R:\n", R)
    print("平移向量 tvec:\n", tvec)
    print("外参矩阵 [R | t]:\n", extrinsic_matrix)
    print("内点数量:\n", len(inliers))


if __name__ == '__main__':
    main()
