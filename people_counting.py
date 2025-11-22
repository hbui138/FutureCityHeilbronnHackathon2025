import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import Tracker

def people_counting(area1,
                    area2,
                    TIME_PER_CUSTOMER: int=30,
                    MODEL_PATH: str='people_counting_weights.pt',
                    VIDEO_PATH: str=None,
                    register_line_area=None,
                    LOG_PATH: str=None,
                    show_video: bool=False) -> bool:
    """
    Logs and prints the amount of people who entered, left and are inside a given space,
    as well as the average waiting time at a given register.

    Parameters:
    - TIME_PER_CUSTOMER (int): Estimated time per customer in seconds.
    - MODEL_PATH (str): Path to the YOLO model for detection.
    - VIDEO_PATH (str): Path to the video file to be processed.
    - area1 (list): Coordinates for the inside area (polygon).
    - area2 (list): Coordinates for the outside area (polygon).
    - register_line_area (list): Coordinates for the rectangle to count people inside.
    - LOG_PATH (str): Path to the file results should be logged to.
    - show_video (boolean): Turns live display of processed frames on or off.

    Returns:
    - True if inference was successful
    - False if an error occurred
    """

    if VIDEO_PATH is None or MODEL_PATH is None:
        print('No proper Paths provided')
        return False

    # Default areas if not provided for test
    if area1 is None:
        area1 = [(0, 0), (1, 0), (0, 1), (1, 1)]  # Inside area
    if area2 is None:
        area2 = [(0, 0), (1, 0), (0, 1), (1, 1)]  # Outside area
    if register_line_area is None:
        register_line_area = [(0, 0), (1, 1)]  # Register line area
    print(area1, area2)

    # Load YOLO model
    model = YOLO(MODEL_PATH)

    # Initialize tracker
    tracker = Tracker()

    # Initialize sets to track entering and exiting people
    entering = set()
    exiting = set()

    # Open video capture
    cap = cv2.VideoCapture(VIDEO_PATH)

    # Function to check if a bounding box is inside the defined rectangle
    def is_inside_rect(bbox, rect):
        x1, y1, x2, y2 = bbox  # Bounding box coordinates (x1, y1, x2, y2)
        rect_x1, rect_y1 = rect[0]  # Top-left corner of the rectangle
        rect_x2, rect_y2 = rect[1]  # Bottom-right corner of the rectangle

        # Check if the bounding box intersects or is inside the rectangle
        return x1 >= rect_x1 and y1 >= rect_y1 and x2 <= rect_x2 and y2 <= rect_y2

    # Count frame number and customer queue
    count = 0
    customer_queue = []

    log_file = None
    if LOG_PATH:
        log_file = open(LOG_PATH, "w")

    # Main loop to process video frames
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("The video capture has ended || Any other error with the camera source")
            return False

        count += 1
        if count % 2 != 0:
            continue

        # Resize frame
        x, y = 393, 700
        frame = cv2.resize(frame, (x, y))

        # Perform object detection with YOLO
        results = model.predict(frame, verbose=False)

        # Extract bounding boxes and associated class IDs
        a = results[0].boxes.xyxy  # Use the 'xyxy' attribute for bounding boxes
        px = pd.DataFrame(a).astype("float")

        detected_people = []

        # Loop through the detections and filter for 'person' class
        for index, row in px.iterrows():
            # Unpack only the bounding box coordinates
            x1, y1, x2, y2 = row

            class_name = "person"  # Retrieve class name from coco.txt

            if 'person' in class_name:
                detected_people.append([int(x1), int(y1), int(x2), int(y2)])

                # Draw bounding boxes around detected people
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        # Update tracker with bounding boxes
        bbox_id = tracker.update(detected_people)

        # Initialize count for people inside the rectangle
        people_in_rect_count = 0

        for bbox in bbox_id:
            x3, y3, x4, y4, person_id = bbox

            # Track position (xt, yt) of the person
            xt, yt = x4, y4

            # People entering the inside area (area2 -> area1)
            if cv2.pointPolygonTest(np.array(area2, np.int32), (xt, yt), False) >= 0:
                entering.add(person_id)

            # People exiting (area1 -> area2)
            if person_id in entering:
                if cv2.pointPolygonTest(np.array(area1, np.int32), (xt, yt), False) >= 0:
                    exiting.add(person_id)

            # Count people inside the defined rectangle
            if is_inside_rect([x3, y3, x4, y4], register_line_area):
                people_in_rect_count += 1

        # Output: Number of people who entered, exited, and are still inside
        num_entered = len(entering)
        num_exited = len(exiting)
        num_inside = num_entered - num_exited

        # Update queue for averaging
        if len(customer_queue) < 100:
            customer_queue.append(people_in_rect_count)
            avg_queue_length = sum(customer_queue) / len(customer_queue)
        else:
            customer_queue.pop(0)
            customer_queue.append(people_in_rect_count)
            avg_queue_length = sum(customer_queue) / len(customer_queue)

        # log/print counts every 10 frames
        if count % 10 == 0:
            log_message = (f"Frame: {count}\n"
                           f"People Entered: {num_entered}\n"
                           f"People Exited: {num_exited}\n"
                           f"People Inside: {num_inside}\n"
                           f"Estimated waiting time: {int(avg_queue_length * TIME_PER_CUSTOMER)} seconds\n\n")
            print(log_message)  # Print to console
            if log_file:
                log_file.write(log_message)  # Write to log file

        # Draw areas (polygons) for inside, outside, and register line
        cv2.polylines(frame, [np.array(area1, np.int32)], isClosed=True, color=(0, 255, 255), thickness=2)
        cv2.polylines(frame, [np.array(area2, np.int32)], isClosed=True, color=(255, 0, 0), thickness=2)
        cv2.rectangle(frame, tuple(register_line_area[0]), tuple(register_line_area[1]), (0, 0, 255), 2)

        if show_video:
            cv2.imshow("Frame", frame)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close all windows
    cap.release()
    cv2.destroyAllWindows()
    return True
