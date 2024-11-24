import cv2
import os


def extract_frames(video_path, image_folder, quality=95):
    """
    Extract frames from a video and save them as JPEG images.

    Parameters:
    - video_path: Path to the input video file.
    - image_folder: Directory where the extracted frames will be saved.
    - quality: JPEG quality of the saved images (0-100). Default is 95.
    """
    print("Starting frame extraction...")

    # 视频捕获
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    # 如果文件夹不存在，则创建
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    n = 1
    while True:
        success, frame = cap.read()
        if not success:
            break

        # 使用os.path.join来确保路径的正确性
        image_path = os.path.join(
            image_folder, f"frame_{n:04d}.jpg")  # 使用4位数的编号

        # 保存JPEG图像时设置质量
        cv2.imwrite(image_path, frame, [
                    int(cv2.IMWRITE_JPEG_QUALITY), quality])

        n += 1

    # 释放视频捕获资源
    cap.release()

    print(f"Frame extraction completed. Total frames extracted: {n-1}")


def main():
    video_path = r"C:\Users\sunaxiang\Desktop\calibration\video\2024_04_09_15_25_12_129.mp4"
    image_folder = r"C:\Users\sunaxiang\Desktop\calibration\image"
    quality = 95  # JPEG图像质量

    extract_frames(video_path, image_folder, quality)


if __name__ == "__main__":
    main()
