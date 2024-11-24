import cv2
import numpy as np
import pandas as pd
from scipy.optimize import least_squares


def cost_function(params, radar_points, camera_points, camera_matrix):
    """
    Define the cost function for optimization.

    Parameters:
    params (np.array): Array containing rotation and translation parameters
    radar_points (np.array): Radar point cloud data
    camera_points (np.array): Pixel points in the camera image
    camera_matrix (np.array): Camera intrinsic matrix

    Returns:
    np.array: Error between projected points and camera pixel points
    """
    # Extract rotation vector and translation vector
    rotation_vector = params[:3]
    translation_vector = params[3:]

    # Convert rotation vector to rotation matrix
    rotation_matrix = cv2.Rodrigues(rotation_vector)[0]

    # Compute radar points projected into camera coordinate system
    radar_points_homogeneous = np.hstack(
        (radar_points, np.ones((radar_points.shape[0], 1))))
    projected_points_homogeneous = np.dot(radar_points_homogeneous, np.hstack(
        (rotation_matrix, translation_vector.reshape(-1, 1))).T)
    projected_points_homogeneous = np.dot(
        projected_points_homogeneous, camera_matrix.T)
    projected_points = projected_points_homogeneous[:,
                                                    :2] / projected_points_homogeneous[:, 2:]

    # Calculate error between predicted points and actual points
    return (projected_points - camera_points).flatten()


def calibrate_extrinsics(radar_points, camera_points, camera_matrix):
    """
    Calibrate extrinsic parameters using RANSAC and optimization.

    Parameters:
    radar_points (np.array): Radar point cloud data
    camera_points (np.array): Pixel points in the camera image
    camera_matrix (np.array): Camera intrinsic matrix

    Returns:
    tuple: Optimized rotation matrix, translation vector
    """
    # Ensure we have at least 4 points
    if radar_points.shape[0] < 4 or camera_points.shape[0] < 4:
        raise ValueError("At least 4 point pairs are required for PnP RANSAC.")

    # Ensure data types are correct
    if radar_points.dtype != np.float32 or camera_points.dtype != np.float32:
        raise ValueError(
            "Radar points and camera points must be of type float32.")

    # Use solvePnPRansac for initial estimation
    success, rvec, tvec, inliers = cv2.solvePnPRansac(
        radar_points, camera_points, camera_matrix,
        distCoeffs=None,
        reprojectionError=100,  # 增大误差阈值以更宽松的标准选择内点
        confidence=0.999,        # 提高置信度以增加算法找到正确解的可能性
        iterationsCount=1000,   # 增加迭代次数以提高结果的稳定性
        flags=cv2.USAC_DEFAULT  # 选择不同的算法来优化内点选择
        # flags=cv2.SOLVEPNP_ITERATIVE  # 选择不同的算法来优化内点选择

        #       USAC_DEFAULT = 32, //!< USAC algorithm, default settings
        #       USAC_PARALLEL = 33, //!< USAC, parallel version
        #       USAC_FM_8PTS = 34,  //!< USAC, fundamental matrix 8 points
        #       USAC_FAST = 35,     //!< USAC, fast settings
        #       USAC_ACCURATE = 36, //!< USAC, accurate settings
        #       USAC_PROSAC = 37,   //!< USAC, sorted points, runs PROSAC
        #       USAC_MAGSAC = 38 //!< USAC, runs MAGSAC++

    )

    if not success:
        raise Exception("PnP RANSAC failed to find a valid solution")

    # Extract inlier radar and camera points
    inlier_radar_points = radar_points[inliers[:, 0]]
    inlier_camera_points = camera_points[inliers[:, 0]]

    initial_params = np.hstack((rvec.flatten(), tvec.flatten()))

    # Use Levenberg-Marquardt/TRF algorithm for refinement based on inliers
    result = least_squares(
        cost_function,                    # 目标函数
        initial_params,                   # 初始参数 (旋转向量和平移向量)
        # args=(inlier_radar_points, inlier_camera_points,
        #       camera_matrix),  # 传递给目标函数的其他参数
        args=(radar_points, camera_points, camera_matrix),
        method='lm',                     # 使用 Trust Region Reflective 方法
        ftol=1e-10,                        # 函数容差
        xtol=1e-10,                        # 参数向量容差
        gtol=1e-10,                        # 梯度容差
        max_nfev=1000,                    # 最大函数评估次数
        verbose=2,
    )

    # 使用 trf 方法进行优化
    # result = least_squares(
    #     cost_function,                      # 目标函数，计算残差的函数
    #     initial_params,                     # 初始参数，包含旋转向量和平移向量
    #     # args=(radar_points, camera_points, camera_matrix),  # 传递给目标函数的其他参数
    #     args=(inlier_radar_points, inlier_camera_points,
    #           camera_matrix),  # 传递给目标函数的其他参数
    #     # 优化方法 ('trf': Trust Region Reflective, 'dogbox': Dogleg, 'lm': Levenberg-Marquardt)
    #     method='trf',
    #     ftol=1e-10,                          # 函数容差，终止条件之一，控制残差的精度
    #     xtol=1e-10,                          # 参数向量容差，终止条件之一，控制优化变量的精度
    #     gtol=1e-10,                          # 梯度容差，终止条件之一，控制梯度的精度
    #     max_nfev=10000,                      # 最大函数调用次数，限制优化迭代次数
    #     # 使用 LSMR 作为信赖域子问题的求解器 ('exact' 或 'lsmr')
    #     tr_solver='exact',
    #     # 损失函数类型 ('linear', 'soft_l1', 'huber', 'cauchy', 'arctan')
    #     loss='huber',
    #     f_scale=1.0,                        # 损失函数缩放因子，用于非线性损失函数调整灵敏度
    #     # 雅可比矩阵估计 ('2-point', '3-point', 'cs' 或者显式指定雅可比函数)
    #     jac='3-point',
    #     # 参数边界，限制参数的搜索范围 (lower_bounds, upper_bounds)
    #     bounds=(-np.inf, np.inf),
    #     verbose=2,                          # 输出详细程度 (0: 不输出, 1: 每步输出, 2: 详细输出)
    #     diff_step=1e-8                      # 数值差分步长，用于计算雅可比矩阵的精度
    # )

    if not result.success:
        raise Exception("Levenberg-Marquardt optimization failed")

    optimized_params = result.x
    rotation_matrix = cv2.Rodrigues(optimized_params[:3])[0]
    translation_vector = optimized_params[3:]

    return rotation_matrix, translation_vector, rvec, tvec, inliers, inlier_radar_points, inlier_camera_points


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

    print("\n")
    print("Radar points loaded:")
    print_data_points(radar_points)
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

    print("Camera points loaded:")
    print_data_points(camera_points)
    return camera_points


def print_data_points(points):
    """
    Print the first and last three data points with ellipsis in the middle.

    Parameters:
    points (np.array): Array of data points
    """
    num_points = points.shape[0]
    if (num_points > 6):
        points_to_print = np.vstack(
            [points[:3], [["..."] * points.shape[1]], points[-3:]])
    else:
        points_to_print = points

    for point in points_to_print:
        formatted_point = "[" + " ".join(f"{p:<12}" for p in point) + "]"
        print(formatted_point)


def print_matrix(matrix, name):
    """
    Print a matrix with a specific format.

    Parameters:
    matrix (np.array): Matrix to be printed
    name (str): Name of the matrix (for printing)
    """
    print(f"{name}:")
    for row in matrix:
        print("[" + " ".join(f"{val:12.8f}" for val in row) + "]")


def print_vector(vector, name):
    """
    Print a vector with a specific format.

    Parameters:
    vector (np.array): Vector to be printed
    name (str): Name of the vector (for printing)
    """
    print(f"{name}:")
    print("[" + " ".join(f"{val:12.8f}" for val in vector) + "]")


def main():
    # Define camera intrinsic matrix (example values, needs actual calibration)
    fx, fy, cx, cy = 957.01226348, 934.81781967, 982.79102164, 499.9173914
    camera_matrix = np.array(
        [[fx, 0, cx],
         [0, fy, cy],
         [0, 0, 1]], dtype=np.float32)

    # Directly specify the paths to the CSV files
    radar_csv_path = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\pointcloud\csv\representative_points.csv'
    camera_csv_path = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\image\csv\camera_incenter.csv'

    # Load radar point cloud and camera pixel point pairs from CSV files
    radar_points = load_radar_points(radar_csv_path)
    camera_points = load_camera_points(camera_csv_path)

    # Check if the number of radar points matches the number of camera points
    if radar_points.shape[0] != camera_points.shape[0]:
        raise ValueError(
            "Number of radar points does not match number of camera points")

    # Calibrate extrinsic parameters
    try:
        rotation_matrix, translation_vector, rvec, tvec, inliers, inlier_radar_points, inlier_camera_points = calibrate_extrinsics(
            radar_points, camera_points, camera_matrix)

        print("\n")

        print(f"Number of inliers: {len(inliers)}")
        # Print inliers' indices
        print("Inlier frame indices:")
        print(inliers[:, 0])

        # Print inliers' radar and camera points
        print("Inlier radar points:")
        print_data_points(inlier_radar_points)
        print("Inlier camera points:")
        print_data_points(inlier_camera_points)

        print("\n")

        # Convert initial rotation vector to rotation matrix for comparison
        initial_rotation_matrix = cv2.Rodrigues(rvec)[0]
        print("Initial rotation matrix from PnP RANSAC:")
        print_matrix(initial_rotation_matrix, "Rotation Matrix")
        # Print initial PnP RANSAC results
        print("Initial PnP RANSAC rotation vector:")
        print_vector(rvec.flatten(), "Rotation Vector (rvec)")
        print("Initial PnP RANSAC translation vector:")
        print_vector(tvec.flatten(), "Translation Vector (tvec)")

        print("\n")

        # Print optimized results
        print("Optimized rotation matrix:")
        print_matrix(rotation_matrix, "Rotation Matrix")
        print("Optimized translation vector:")
        print_vector(translation_vector, "Translation Vector")

        print("\n")

    except Exception as e:
        print(f"Calibration failed: {e}")


if __name__ == "__main__":
    main()
