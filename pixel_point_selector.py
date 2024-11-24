import os
import cv2
import pandas as pd
import numpy as np
import signal
import sys

# Initialize global variables
a = []
b = []
scale = 1.0
offset_x = 0
offset_y = 0
drag_start = None
img_scaled = None
last_scale = scale
win_name = "image"
window_width = 800
window_height = 600
limit_points = True  # Option to limit points selection to 3
max_points = 3  # Maximum points to select if limit_points is True
saved = False  # Flag to track if coordinates and center have been saved


def point(event, x, y, flags, param):
    global scale, offset_x, offset_y, drag_start, img, img_scaled, last_scale, limit_points, saved

    if event == cv2.EVENT_LBUTTONDOWN:
        if limit_points and len(a) >= max_points:
            return
        x_img = int((x - window_width // 2 - offset_x) /
                    scale + img.shape[1] // 2)
        y_img = int((y - window_height // 2 - offset_y) /
                    scale + img.shape[0] // 2)
        a.append(x_img)
        b.append(y_img)
        print(f"Selected point: ({x_img}, {y_img})")
        redraw_image()
        if limit_points and len(a) >= max_points:
            if not saved:
                save_coordinates_and_center()
                saved = True
            # Wait for 1 second before closing the program
            # time.sleep(1)
            # cv2.destroyAllWindows()
            # sys.exit(0)

    elif event == cv2.EVENT_MOUSEWHEEL:
        scale_factor = 1.1 if flags > 0 else 1 / 1.1
        new_scale = scale * scale_factor
        x_center = (x - window_width // 2 - offset_x) / scale
        y_center = (y - window_height // 2 - offset_y) / scale
        offset_x = x - window_width // 2 - x_center * new_scale
        offset_y = y - window_height // 2 - y_center * new_scale
        scale = new_scale
        redraw_image()

    elif event == cv2.EVENT_RBUTTONDOWN:
        drag_start = (x, y)

    elif event == cv2.EVENT_RBUTTONUP:
        drag_start = None

    elif event == cv2.EVENT_MOUSEMOVE:
        if drag_start:
            dx = x - drag_start[0]
            dy = y - drag_start[1]
            offset_x += dx
            offset_y += dy
            drag_start = (x, y)
            redraw_image()


def redraw_image():
    global img, img_scaled, scale, offset_x, offset_y, last_scale, limit_points

    if img_scaled is None or scale != last_scale:
        height, width = img.shape[:2]
        new_dim = (int(width * scale), int(height * scale))
        img_scaled = cv2.resize(img, new_dim, interpolation=cv2.INTER_LINEAR)
        last_scale = scale

    img_display = np.zeros((window_height, window_width, 3), dtype=np.uint8)

    x_center = img_scaled.shape[1] // 2
    y_center = img_scaled.shape[0] // 2
    x_start = int(window_width // 2 - x_center + offset_x)
    y_start = int(window_height // 2 - y_center + offset_y)

    x_end = x_start + img_scaled.shape[1]
    y_end = y_start + img_scaled.shape[0]

    src_x_start = max(0, -x_start)
    src_y_start = max(0, -y_start)
    src_x_end = min(img_scaled.shape[1], window_width - x_start)
    src_y_end = min(img_scaled.shape[0], window_height - y_start)

    dest_x_start = max(0, x_start)
    dest_y_start = max(0, y_start)
    dest_x_end = min(window_width, x_start + img_scaled.shape[1])
    dest_y_end = min(window_height, y_start + img_scaled.shape[0])

    if src_x_start < src_x_end and src_y_start < src_y_end:
        img_display[dest_y_start:dest_y_end, dest_x_start:dest_x_end] = \
            img_scaled[src_y_start:src_y_end, src_x_start:src_x_end]

    for i in range(len(a)):
        x_display = int((a[i] - (img.shape[1] // 2)) *
                        scale + window_width // 2 + offset_x)
        y_display = int((b[i] - (img.shape[0] // 2)) *
                        scale + window_height // 2 + offset_y)
        if 0 <= x_display < img_display.shape[1] and 0 <= y_display < img_display.shape[0]:
            xy = f"{a[i]},{b[i]}"
            cv2.circle(img_display, (x_display, y_display),
                       5, (0, 0, 255), thickness=-1)
            cv2.putText(img_display, xy, (x_display, y_display),
                        cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 0, 0), thickness=2)

    if limit_points and len(a) == 3:
        # Calculate and draw the incenter
        center_x, center_y = calculate_incenter(a, b)
        center_x_display = int(
            (center_x - (img.shape[1] // 2)) * scale + window_width // 2 + offset_x)
        center_y_display = int(
            (center_y - (img.shape[0] // 2)) * scale + window_height // 2 + offset_y)
        if 0 <= center_x_display < img_display.shape[1] and 0 <= center_y_display < img_display.shape[0]:
            cv2.circle(img_display, (center_x_display,
                       center_y_display), 5, (0, 255, 0), thickness=-1)
            cv2.putText(img_display, f"Incenter: ({int(center_x)},{int(center_y)})", (center_x_display, center_y_display),
                        cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 0, 0), thickness=2)

    cv2.imshow(win_name, img_display)


def calculate_incenter(x, y):
    """Calculate the incenter of the triangle."""
    def distance(p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    # Calculate the lengths of the sides of the triangle
    A = distance((x[1], y[1]), (x[2], y[2]))
    B = distance((x[0], y[0]), (x[2], y[2]))
    C = distance((x[0], y[0]), (x[1], y[1]))

    # Calculate the incenter
    P = A + B + C
    x_incenter = (A * x[0] + B * x[1] + C * x[2]) / P
    y_incenter = (A * y[0] + B * y[1] + C * y[2]) / P

    return int(round(x_incenter)), int(round(y_incenter))


def save_coordinates_and_center():
    global img_path, output_dir
    df = pd.DataFrame({
        'Type': ['Point'] * len(a) + ['Incenter'],
        'X': [a[i] for i in range(len(a))] + [calculate_incenter(a, b)[0]],
        'Y': [b[i] for i in range(len(b))] + [calculate_incenter(a, b)[1]]
    })

    os.makedirs(output_dir, exist_ok=True)

    image_name = os.path.splitext(os.path.basename(img_path))[0]
    csv_path = os.path.join(output_dir, f'{image_name}.csv')

    df.to_csv(csv_path, index=False)

    print(f"Coordinates and incenter saved to {csv_path}")


def signal_handler(sig, frame):
    print("Process interrupted by user.")
    cv2.destroyAllWindows()
    sys.exit(0)


def main():
    global img, img_path, limit_points, output_dir, saved

    signal.signal(signal.SIGINT, signal_handler)

    # Set the limit_points flag here
    limit_points = True  # Set to True to limit points to 3, False for no limit
    # limit_points = False  # Set to True to limit points to 3, False for no limit

    # Set input and output paths
    img_path = r'C:\BaiduSyncdisk\Calibration\4DRadar_Moncular_Calibration\4DRadar_Moncular_Calibration\image\frame_100.jpg'
    output_dir = r'C:\BaiduSyncdisk\Calibration\4DRadar_Moncular_Calibration\4DRadar_Moncular_Calibration\image\csv'

    # Load image
    img = cv2.imread(img_path)
    if img is None:
        print("Error loading image.")
        return

    # Set up window
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, window_width, window_height)

    # Initialize display
    redraw_image()

    # Set up mouse callback
    cv2.setMouseCallback(win_name, point)

    # Main loop
    while True:
        key = cv2.waitKey(1)
        if key == 27:  # ESC key
            break

        # Check if window was closed
        if cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    # Ensure the last state is saved and displayed
    if not saved:
        save_coordinates_and_center()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
