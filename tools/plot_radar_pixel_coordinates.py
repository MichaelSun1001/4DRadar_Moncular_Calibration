import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def plot_data(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path)

    # 创建一个图形窗口并设置大小
    plt.figure(figsize=(14, 8))

    # 获取所有点对的坐标
    pixel_x = df['Pixel_X'].values
    pixel_y = df['Pixel_Y'].values
    radar_x = df['Radar_X'].values
    radar_y = df['Radar_Y'].values
    frames = df['Frame'].values

    # 计算坐标差值（偏移量）
    dx = radar_x - pixel_x
    dy = radar_y - pixel_y

    # 添加抖动以避免点重叠
    jitter_strength = 0.5
    pixel_x_jittered = pixel_x + \
        np.random.uniform(-jitter_strength, jitter_strength, size=len(pixel_x))
    pixel_y_jittered = pixel_y + \
        np.random.uniform(-jitter_strength, jitter_strength, size=len(pixel_y))
    radar_x_jittered = radar_x + \
        np.random.uniform(-jitter_strength, jitter_strength, size=len(radar_x))
    radar_y_jittered = radar_y + \
        np.random.uniform(-jitter_strength, jitter_strength, size=len(radar_y))

    # 绘制散点图
    plt.scatter(pixel_x_jittered, pixel_y_jittered, c='blue',
                label='Pixel Coordinates', alpha=0.6)
    plt.scatter(radar_x_jittered, radar_y_jittered, c='red',
                label='Radar Coordinates', alpha=0.6)

    # 使用虚线显示点对之间的偏移量
    for i in range(len(df)):
        plt.plot([pixel_x_jittered[i], radar_x_jittered[i]], [
                 pixel_y_jittered[i], radar_y_jittered[i]], 'k--', alpha=0.7)
        # 调整标签位置以避免重叠
        plt.text(pixel_x_jittered[i], pixel_y_jittered[i],
                 f'F{frames[i]}', fontsize=8, ha='right', va='bottom', color='blue')
        plt.text(radar_x_jittered[i], radar_y_jittered[i],
                 f'F{frames[i]}', fontsize=8, ha='right', va='bottom', color='red')

    plt.title('Pixel and Radar Coordinates with Connections')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.grid(True)

    # 提供更好的缩放体验
    plt.gca().set_aspect('equal', adjustable='box')

    # 显示图形
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    file_path = r"C:\BaiduSyncdisk\Calibration\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\calib\transformed_points.csv"  # 使用原始路径
    plot_data(file_path)
