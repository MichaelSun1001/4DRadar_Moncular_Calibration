import numpy as np
import pandas as pd
import os
import cv2


def transform_radar_to_camera(radar_points, rotation_matrix, translation_vector):
    # Convert radar points to homogeneous coordinates
    ones = np.ones((radar_points.shape[0], 1))
    radar_points_hom = np.hstack((radar_points, ones))

    # Create the transformation matrix
    transform_matrix = np.eye(4)
    transform_matrix[:3, :3] = rotation_matrix
    transform_matrix[:3, 3] = translation_vector

    # Apply the transformation
    camera_points_hom = radar_points_hom.dot(transform_matrix.T)
    camera_points = camera_points_hom[:, :3] / \
        camera_points_hom[:, 3][:, np.newaxis]

    return camera_points


def project_to_image(camera_points, camera_intrinsics):
    # Convert 3D points to 2D image points
    image_points = camera_intrinsics.dot(camera_points.T).T
    image_points = image_points[:, :2] / image_points[:, 2][:, np.newaxis]

    return image_points


def main():
    # Define file paths
    radar_file_path = r'C:\BaiduSyncdisk\Calibration\Radar Monocular Calibration\4DRadar_Moncular_Calibration\dataset\pointcloud\csv\representative_points.csv'
    pixel_file_path = r'C:\BaiduSyncdisk\Calibration\Radar Monocular Calibration\4DRadar_Moncular_Calibration\dataset\image\csv\camera_incenter copy.csv'
    image_folder_path = r'C:\BaiduSyncdisk\Calibration\Radar Monocular Calibration\4DRadar_Moncular_Calibration\dataset\image'
    output_folder_path = r'C:\BaiduSyncdisk\Calibration\Radar Monocular Calibration\4DRadar_Moncular_Calibration\dataset\calib'
    csv_output_path = os.path.join(
        output_folder_path, 'transformed_points.csv')

    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Load radar and pixel data
    radar_data = pd.read_csv(radar_file_path)
    pixel_data = pd.read_csv(pixel_file_path)

    # Calibration matrix parameters

    rotation_matrix = np.array([
        [[0.9204707, - 0.3630727,   0.1446095],
         [0.12279504, - 0.08259498, - 0.9889891],
            [0.37101896,  0.92809282, - 0.03144273]]
    ])
    translation_vector = np.array([-3.05559704, - 1.40092039,  4.29059099])

    # rotation_matrix = np.array([
    #     [[0.93800628, - 0.34658204,  0.00501163],
    #      [-0.03022113, - 0.09617841, - 0.99490522],
    #      [0.34529829,  0.93307588, - 0.10069005]]
    # ])
    # translation_vector = np.array([-2.69305571, - 1.25246701,  3.78221096])

    # rotation_matrix = np.array([
    #     [[0.67633225,   0.73144627, - 0.08695429],
    #      [-0.02264119,   0.13863639,   0.99008451],
    #      [0.73624865, - 0.66765733,   0.11032508]]
    # ])
    # translation_vector = np.array([-3.88822534, - 1.59051264,   5.50254805])

    # rotation_matrix = np.array([
    #     [[0.68710884,   0.61402068,   0.38840706],
    #      [-0.67286229,   0.33608425,   0.65901724],
    #      [0.27411272, - 0.71416104,   0.64407781]]
    # ])
    # translation_vector = np.array([-4.74085961, - 2.27979237,   6.80150260])

    # Camera intrinsic parameters
    fx, fy, cx, cy = 957.01226348, 934.81781967, 982.79102164, 499.9173914
    camera_intrinsics = np.array(
        [[fx, 0, cx],
         [0, fy, cy],
         [0, 0, 1]], dtype=np.float32)

    # Prepare CSV output data list
    output_data = []

    # Process each frame
    for frame_id in radar_data['Frame'].unique():
        try:
            # Extract radar points for the current frame
            radar_points = radar_data[radar_data['Frame'] == frame_id][[
                'Rep_X', 'Rep_Y', 'Rep_Z']].to_numpy()

            # Extract pixel points for the current frame
            pixel_points = pixel_data[pixel_data['Frame'] == frame_id]

            # Transform radar points to camera coordinates
            camera_points = transform_radar_to_camera(
                radar_points, rotation_matrix, translation_vector)

            # Project camera coordinates to image plane
            image_points = project_to_image(camera_points, camera_intrinsics)

            # Load the corresponding image
            image_path = os.path.join(
                image_folder_path, f'frame_{frame_id}.jpg')
            image = cv2.imread(image_path)

            if image is None:
                print(f"Image {image_path} not found.")
                continue

            # Draw the radar points and corresponding pixel points on the image
            for (pixel_x, pixel_y, radar_x, radar_y) in zip(pixel_points['X'], pixel_points['Y'], image_points[:, 0], image_points[:, 1]):
                # Draw pixel points in blue
                cv2.circle(image, (int(pixel_x), int(pixel_y)),
                           5, (255, 0, 0), -1)
                cv2.putText(image, f'({pixel_x}, {pixel_y})', (int(
                    pixel_x) + 10, int(pixel_y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                # Draw radar points in red
                cv2.circle(image, (int(radar_x), int(radar_y)),
                           5, (0, 0, 255), -1)
                cv2.putText(image, f'({int(radar_x)}, {int(radar_y)})', (int(
                    radar_x) + 10, int(radar_y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                # Optionally, draw a line between corresponding points
                cv2.line(image, (int(pixel_x), int(pixel_y)),
                         (int(radar_x), int(radar_y)), (0, 255, 0), 2)

            # Save the annotated image
            output_image_path = os.path.join(
                output_folder_path, f'annotated_frame_{frame_id}.jpg')
            cv2.imwrite(output_image_path, image)

            # Print and save each frame's data
            for i, (pixel_x, pixel_y, radar_x, radar_y) in enumerate(zip(pixel_points['X'], pixel_points['Y'], image_points[:, 0], image_points[:, 1])):
                print(
                    f"Frame {frame_id}: Pixel_X: {pixel_x}, Pixel_Y: {pixel_y}, Radar_X: {radar_x:.6f}, Radar_Y: {radar_y:.6f}")
                output_data.append(
                    [frame_id, pixel_x, pixel_y, radar_x, radar_y])

        except Exception as e:
            print(f"Error processing frame {frame_id}: {e}")

    # Save the transformed points to a CSV file
    output_df = pd.DataFrame(output_data, columns=[
                             'Frame', 'Pixel_X', 'Pixel_Y', 'Radar_X', 'Radar_Y'])
    output_df.to_csv(csv_output_path, index=False)
    print(f"Transformed points saved to {csv_output_path}")


if __name__ == "__main__":
    main()
