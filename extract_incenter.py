import os
import pandas as pd
import re


def extract_incenter(input_folder):
    # 创建一个空的DataFrame来存储所有Incenter数据
    incenter_df = pd.DataFrame(columns=['Frame', 'Type', 'X', 'Y'])

    # 遍历文件夹中的所有CSV文件
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)
            try:
                # 读取CSV文件
                df = pd.read_csv(file_path)
                # 提取Incenter数据
                incenter_data = df[df['Type'] == 'Incenter'].copy()
                # 提取文件名中的数字作为帧数
                frame_number_match = re.findall(r'\d+', filename)
                if frame_number_match:
                    frame_number = frame_number_match[0]
                    incenter_data.loc[:, 'Frame'] = frame_number
                    # 将Incenter数据添加到总的DataFrame中
                    incenter_df = pd.concat(
                        [incenter_df, incenter_data], ignore_index=True)
            except Exception as e:
                print(f"处理文件 {filename} 时出错: {e}")

    return incenter_df


def main():
    # 输入路径
    # 修改为你的CSV文件夹路径
    input_folder = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\4DRadar_Moncular_Calibration\dataset\image\csv'

    # 输出文件路径
    output_file = os.path.join(input_folder, 'camera_incenter.csv')

    # 如果输出文件存在，删除它
    if os.path.exists(output_file):
        os.remove(output_file)

    # 提取Incenter数据
    incenter_df = extract_incenter(input_folder)

    # 调整列顺序
    incenter_df = incenter_df[['Frame',  'X', 'Y']]

    # 对数据按Frame列排序
    incenter_df['Frame'] = incenter_df['Frame'].astype(int)  # 确保Frame列是整数类型
    incenter_df = incenter_df.sort_values(by='Frame')

    # 将所有Incenter数据写入一个新的CSV文件
    incenter_df.to_csv(output_file, index=False)

    print(f"所有Incenter数据已成功写入 {output_file}")


if __name__ == "__main__":
    main()
