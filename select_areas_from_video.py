import cv2

click_points = []
current_area = "Area 1: Inside"

def select_points(event, x, y, flags, param):
    global click_points, current_area


    if event == cv2.EVENT_LBUTTONDOWN:
        # Store clicked point
        click_points.append((x, y))
        print(f"Point selected: ({x}, {y})")

        # Update current area based on points clicked
        if len(click_points) == 4:
            current_area = "Area 2: Outside"
        elif len(click_points) == 8:
            current_area = "Register Line: Click to define"
        elif len(click_points) == 10:
            current_area = "Done"

def select_areas_from_video(video_path):
    """
    Used to mark the areas needed for inference
    :param:
    video_path(str): Path to the Video later to be used to do inference on
    :return:
    area1, area2 and register_line_area used for counting people and measuring waiting tim
    """
    global click_points, current_area

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error opening video")
        return None, None, None

    ret, frame = cap.read()
    if not ret:
        print("Error reading first frame")
        return None, None, None

    # Resize to model size
    resize_width, resize_height = 393, 700
    frame_original = cv2.resize(frame, (resize_width, resize_height))

    cv2.imshow("Select Areas", frame_original)
    cv2.setMouseCallback("Select Areas", select_points, param=frame_original)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    color = (255, 255, 255)
    thickness = 2

    while True:
        # Make a fresh copy to redraw points and message
        frame_display = frame_original.copy()

        # Draw all clicked points
        for pt in click_points:
            cv2.circle(frame_display, pt, 5, (0, 255, 0), -1)

        # Draw message at top
        cv2.putText(frame_display, current_area, (10, 30), font, font_scale, color, thickness)

        cv2.imshow("Select Areas", frame_display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or len(click_points) >= 10:
            break

    cv2.destroyAllWindows()

    area1 = click_points[:4]
    area2 = click_points[4:8]
    register_line_area = [click_points[8], click_points[9]]

    print(f"Area 1: {area1}")
    print(f"Area 2: {area2}")
    print(f"Register Line Area: {register_line_area}")

    return area1, area2, register_line_area

select_areas_from_video('test_1.mp4')