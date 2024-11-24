import csv
import os


def process_csv(input_file, output_file):
    # 读取输入 CSV 文件
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)

        # 处理数据
        processed_data = []
        for row in reader:
            frame_number = int(row['frame_number'])
            index = int(row['point_number']) - 1  # 假设 point_number 从 1 开始
            snr = float(row['SNR'])
            x = float(row['X'])
            y = float(row['Y'])
            z = float(row['Z'])
            processed_data.append([frame_number, index, snr, x, y, z])

    # 将处理后的数据写入输出 CSV 文件
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        # 写入标题行
        writer.writerow(['Frame', 'Index', 'SNR', 'X', 'Y', 'Z'])
        writer.writerows(processed_data)

    print(f"处理后的数据已保存到 {output_file}")


def main():
    # 输入 CSV 文件的路径
    input_file = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\pointcloud\calibration_data.csv'
    # 输出文件夹的路径
    output_folder = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\pointcloud\csv'

    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 定义输出文件路径
    output_file = os.path.join(output_folder, 'pointcloud.csv')

    # 处理 CSV 文件
    process_csv(input_file, output_file)


if __name__ == "__main__":
    main()
