import cv2
import csv

# 设置图片路径
image_path = r'C:\Users\sunaxiang\Desktop\Radar_Moncular_Calibration\3DRadar_Moncular_Calibration\dataset\image\frame_59.jpg'
output_csv = r'C:\Users\sunaxiang\Desktop\output_coordinates.csv'

# 读取图像
img = cv2.imread(image_path)
if img is None:
    print("无法加载图像，请检查路径")
    exit()

# 存储坐标的列表
points = []


def point(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        points.append((x, y))
        cv2.circle(img, (x, y), 5, (0, 0, 255), thickness=-1)
        cv2.putText(img, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    1.0, (255, 0, 0), thickness=1)
        cv2.imshow("image", img)
        print(f"当前坐标: {points}")


cv2.namedWindow("image")
cv2.setMouseCallback("image", point)
cv2.imshow("image", img)

# 按 's' 键保存坐标并退出，按 'q' 键直接退出
while True:
    key = cv2.waitKey(1) & 0xFF

    # 检查窗口是否关闭
    if cv2.getWindowProperty("image", cv2.WND_PROP_VISIBLE) < 1:
        break

    if key == ord('s'):
        # 保存坐标到CSV文件
        with open(output_csv, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["X", "Y"])
            writer.writerows(points)
        print(f"坐标已保存到 {output_csv}")
        break
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
