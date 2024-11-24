import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import distance
from sklearn.cluster import KMeans


def save_point_cloud_data_to_csv(data, csv_filename):
    """Save point cloud data to a CSV file"""
    df = pd.DataFrame(data)
    df.to_csv(csv_filename, index=False)


def plot_point_cloud(frame_data, output_path, frame_number):
    """Plot and save the point cloud for the current frame"""
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    xs = frame_data["X"]
    ys = frame_data["Y"]
    zs = frame_data["Z"]
    snrs = frame_data["SNR"]
    indices = frame_data.index

    scatter = ax.scatter(xs, ys, zs, c=snrs, cmap="viridis", marker='o')

    for i, (x, y, z) in enumerate(zip(xs, ys, zs)):
        ax.text(x, y, z, f'{indices[i]}', fontsize=9)

    plt.colorbar(scatter, ax=ax, label='SNR')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Z Coordinate')
    ax.set_title(f'Point Cloud Data for Frame {frame_number}')

    frame_filename = f"frame_{frame_number}_point_cloud.png"
    frame_filepath = os.path.join(output_path, frame_filename)
    plt.savefig(frame_filepath)
    plt.close()


def find_representative_point_with_weighted_average(frame_data):
    """Calculate a representative point using weighted average"""
    coords = frame_data[["X", "Y", "Z"]].values
    snrs = frame_data["SNR"].values  # Use SNR as weights

    if len(coords) < 1:
        return None

    # Normalize SNR values to be in a reasonable range for weighting
    weights = snrs / snrs.sum()

    # Compute the weighted average
    representative_point = np.average(coords, axis=0, weights=weights)
    return representative_point


def find_representative_point_with_distances(frame_data):
    """Calculate a representative point based on distances"""
    coords = frame_data[["X", "Y", "Z"]].values
    num_points = len(coords)

    if num_points < 3:
        return None

    # Compute distance matrix
    dist_matrix = distance.cdist(coords, coords, 'euclidean')
    np.fill_diagonal(dist_matrix, np.inf)  # Ignore self-distances

    # Determine the number of closest points to consider
    num_closest_points = int(num_points * 4 / 5)

    # Find the indices of the smallest distances
    min_dist_indices = dist_matrix.argsort(axis=None)[:num_closest_points]
    min_dist_points = np.unravel_index(min_dist_indices, dist_matrix.shape)

    # Extract the coordinates of these points
    points = coords[min_dist_points[0]]

    # Calculate the average coordinate
    representative_point = points.mean(axis=0)
    return representative_point


def find_representative_point_with_kmeans(frame_data):
    """Calculate a representative point using K-means clustering"""
    coords = frame_data[["X", "Y", "Z"]].values

    if len(coords) < 1:
        return None

    # Perform K-means clustering with 1 cluster to find the centroid
    kmeans = KMeans(n_clusters=1, random_state=0).fit(coords)
    representative_point = kmeans.cluster_centers_[0]
    return representative_point


def main(input_csv, output_directory, method='weighted_average'):
    """Main function to process point cloud data and generate output files"""
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Read CSV file and strip potential whitespace characters
    df = pd.read_csv(input_csv, skipinitialspace=True)

    # Ensure column names are correct
    df.columns = df.columns.str.strip()

    # Group data by frame
    frames = df.groupby('Frame')

    representative_points = []

    for frame, frame_data in frames:
        frame_data = frame_data.reset_index(drop=True)  # Reset index

        # Plot and save the point cloud for the current frame
        plot_point_cloud(frame_data, output_directory, frame)

        # Calculate the representative point using the selected method
        if method == 'weighted_average':
            representative_point = find_representative_point_with_weighted_average(
                frame_data)
        elif method == 'distances':
            representative_point = find_representative_point_with_distances(
                frame_data)
        elif method == 'kmeans':
            representative_point = find_representative_point_with_kmeans(
                frame_data)
        else:
            raise ValueError(f"Unknown method: {method}")

        if representative_point is not None:
            representative_points.append({
                "Frame": frame,
                "Rep_X": representative_point[0],
                "Rep_Y": representative_point[1],
                "Rep_Z": representative_point[2]
            })
        else:
            print(
                f"Frame {frame} does not have enough points to calculate a representative point.")

    # Save representative points data to a new CSV file
    rep_csv_filename = os.path.join(
        output_directory, "representative_points.csv")
    save_point_cloud_data_to_csv(representative_points, rep_csv_filename)


if __name__ == "__main__":
    # Set input CSV file path and output directory
    input_csv = r"C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\pointcloud\csv\pointcloud.csv"
    output_path = r"C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\pointcloud\csv"

    # Specify method: 'weighted_average', 'distances', or 'kmeans'
    # Change to 'distances' or 'kmeans' to use the other methods
    method = 'distances'

    main(input_csv, output_path, method)


# 加权平均法(weighted_average)：
# 适用情况：点云的信噪比(SNR) 数据准确，并且 SNR 能够反映点的权重（即高 SNR 表示更重要的点）。
# 优点：能够利用 SNR 信息，使得计算的代表点更具有物理意义。
# 缺点：如果 SNR 数据不准确或不稳定，结果可能会受到影响。

# 距离最小法(distances)：
# 适用情况：点云数据中存在较多的噪声，但总体上点分布较为集中。
# 优点：通过选择距离最小的 n*3/4 个点，可以减少噪声点对代表点的影响。
# 缺点：如果点云数据本身非常分散或者有多个聚类中心，这种方法可能不太适合。

# K-means 聚类法(kmeans)：
# 适用情况：点云数据具有明显的聚类特性，并且希望通过聚类算法找到中心点。
# 优点：能够有效处理聚类特性的点云数据，并找到聚类中心作为代表点。
# 缺点：对噪声敏感，且需要设定聚类数量（这里设定为 1，找到单个中心点）。
