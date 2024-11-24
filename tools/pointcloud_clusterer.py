import pandas as pd
import numpy as np
import open3d as o3d
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt


def read_csv(file_path):
    """
    Read CSV file and return a DataFrame containing point cloud data.
    """
    try:
        data = pd.read_csv(file_path)
        print(f"Data read successfully from {file_path}.")
        return data
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return None


def plot_k_distance(data, k):
    """
    Plot k-distance graph to help choose `eps` parameter.
    """
    try:
        nbrs = NearestNeighbors(n_neighbors=k).fit(data[['X_m', 'Y_m', 'Z_m']])
        distances, indices = nbrs.kneighbors(data[['X_m', 'Y_m', 'Z_m']])
        distances = np.sort(distances[:, k-1], axis=0)
        plt.figure(figsize=(10, 5))
        plt.plot(distances)
        plt.title('k-Distance Graph')
        plt.xlabel('Point Index')
        plt.ylabel(f'{k}-Distance')
        plt.grid(True)
        plt.show()
        return distances
    except Exception as e:
        print(f"Error plotting k-distance graph: {e}")
        return None


def cluster_points(data, eps, min_samples):
    """
    Perform clustering on point cloud data.
    """
    try:
        clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(
            data[['X_m', 'Y_m', 'Z_m']])
        data['cluster'] = clustering.labels_
        print(
            f"Clustering completed with eps={eps} and min_samples={min_samples}.")
        return data
    except Exception as e:
        print(f"Error during clustering: {e}")
        return pd.DataFrame()


def visualize_points(points, window_name, is_clustered=False):
    """
    Visualize point cloud data using Open3D.
    """
    try:
        print(f"Visualizing points in window: {window_name}")
        point_cloud = o3d.geometry.PointCloud()
        points_data = points[['X_m', 'Y_m', 'Z_m']].values
        point_cloud.points = o3d.utility.Vector3dVector(points_data)

        if is_clustered:
            colors = np.array([[0.0, 0.0, 1.0] if label == -
                              1 else [1.0, 0.0, 0.0] for label in points['cluster']])
            point_cloud.colors = o3d.utility.Vector3dVector(colors)
        else:
            # Original point cloud in gray
            point_cloud.paint_uniform_color([0.5, 0.5, 0.5])

        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name=window_name)
        vis.add_geometry(point_cloud)
        vis.run()
        vis.destroy_window()
    except Exception as e:
        print(f"Error during visualization of points: {e}")


def visualize_individual_clusters(clustered_points):
    """
    Visualize red and blue points separately in two new windows using Open3D.
    """
    try:
        print("Visualizing individual clusters.")
        # Red points (clustered points)
        red_points = clustered_points[clustered_points['cluster'] != -1]
        red_point_cloud = o3d.geometry.PointCloud()
        red_points_data = red_points[['X_m', 'Y_m', 'Z_m']].values
        red_point_cloud.points = o3d.utility.Vector3dVector(red_points_data)
        red_point_cloud.paint_uniform_color([1.0, 0.0, 0.0])  # Red

        # Blue points (noise points)
        blue_points = clustered_points[clustered_points['cluster'] == -1]
        blue_point_cloud = o3d.geometry.PointCloud()
        blue_points_data = blue_points[['X_m', 'Y_m', 'Z_m']].values
        blue_point_cloud.points = o3d.utility.Vector3dVector(blue_points_data)
        blue_point_cloud.paint_uniform_color([0.0, 0.0, 1.0])  # Blue

        # Visualize red points
        vis_red = o3d.visualization.Visualizer()
        vis_red.create_window(window_name="Red Points")
        vis_red.add_geometry(red_point_cloud)
        vis_red.run()
        vis_red.destroy_window()

        # Visualize blue points
        vis_blue = o3d.visualization.Visualizer()
        vis_blue.create_window(window_name="Blue Points")
        vis_blue.add_geometry(blue_point_cloud)
        vis_blue.run()
        vis_blue.destroy_window()
    except Exception as e:
        print(f"Error during visualization of individual clusters: {e}")


def save_to_csv(data, output_file_path):
    """
    Save clustered point cloud data to CSV file.
    """
    try:
        data.to_csv(output_file_path, index=False)
        print(f"Data saved to {output_file_path}.")
    except Exception as e:
        print(f"Error saving to CSV file: {e}")


def main():
    # File paths
    input_file_path = r'C:\Users\sunaxiang\Desktop\calibration\point_cloud\radar_points.csv'
    output_file_path = r'C:\Users\sunaxiang\Desktop\calibration\point_cloud\clustered_points.csv'

    # Read point cloud data
    data = read_csv(input_file_path)
    if data is None:
        return

    # Plot k-distance graph
    min_samples = 10
    k = min_samples - 1  # Usually set to min_samples - 1
    distances = plot_k_distance(data, k)

    if distances is None:
        return

    # Manually set eps value based on k-distance graph
    eps = 6  # Adjust this value based on the k-distance graph

    # Visualize original point cloud
    visualize_points(data, "Original Points")

    # Perform clustering
    clustered_points = cluster_points(data, eps, min_samples)
    if not clustered_points.empty:
        print("Clustered Points:")
        print(clustered_points)
        # Save clustered point cloud data to CSV file
        save_to_csv(clustered_points, output_file_path)
        # Visualize clustered point cloud
        visualize_points(clustered_points, "Clustered Points",
                         is_clustered=True)
        # Visualize red and blue points separately
        visualize_individual_clusters(clustered_points)
    else:
        print("No clusters found with the given clustering criteria.")


if __name__ == '__main__':
    main()
