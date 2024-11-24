from PIL import Image
import os

# 输入 BMP 文件所在的文件夹路径
input_folder = r"C:\Users\10137\Desktop\1119yanzheng"
# 输出 JPG 文件保存的文件夹路径
output_folder = r"C:\Users\10137\Desktop\1119yanzheng-jpg"

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 遍历输入文件夹中的所有 BMP 文件
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(".bmp"):  # 检查是否是 BMP 文件
        bmp_path = os.path.join(input_folder, file_name)
        jpg_path = os.path.join(output_folder, file_name.rsplit(".", 1)[0] + ".jpg")
        
        try:
            # 打开 BMP 文件并转换为 JPG
            with Image.open(bmp_path) as img:
                img = img.convert("RGB")  # 确保没有 alpha 通道
                img.save(jpg_path, "JPEG")
            print(f"Converted: {bmp_path} -> {jpg_path}")
        except Exception as e:
            print(f"Failed to convert {bmp_path}: {e}")

print("All conversions completed!")
