import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import Tracker
import json  # Import the JSON module

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

    if LOG_PATH is None:
        LOG_PATH = VIDEO_PATH.split('.')[0] + ".json"

    if area1 is None:
        area1 = [(0, 0), (1, 0), (1, 1), (0, 1)]  # A 1x1 pixel square
    if area2 is None:
        area2 = [(0, 0), (1, 0), (1, 1), (0, 1)]  # A 1x1 pixel square
    if register_line_area is None:
        register_line_area = [(0, 0), (1, 1)]  # A tiny rectangle

    # Print areas for debugging
    print(f"Inside area (area1): {area1}")
    print(f"Outside area (area2): {area2}")
    print(f"Register line area: {register_line_area}")

    # Load YOLO model
    model = YOLO(MODEL_PATH)

    # Initialize tracker
    tracker = Tracker()

    # Initialize sets to track entering and exiting people
    entering = set()
    exiting = set()

    # Open video capture
    cap = cv2.VideoCapture(VIDEO_PATH)

    # Check if video is opened correctly
    if not cap.isOpened():
        print("Error opening video stream or file")
        return False

    # Function to check if a bounding box is inside the defined rectangle
    def is_inside_rect(bbox, rect):
        x1, y1, x2, y2 = bbox
        rect_x1, rect_y1 = rect[0]
        rect_x2, rect_y2 = rect[1]
        return x1 >= rect_x1 and y1 >= rect_y1 and x2 <= rect_x2 and y2 <= rect_y2

    # Count frame number and customer queue
    count = 0
    customer_queue = []

    # Initialize log list for JSON output
    log_data = []

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Error reading frame")
            break

        count += 1
        if count % 2 != 0:
            continue

        # Resize frame
        frame = cv2.resize(frame, (393, 700))

        # Perform object detection with YOLO
        results = model.predict(frame, verbose=False)

        # Extract bounding boxes and associated class IDs
        a = results[0].boxes.xyxy
        px = pd.DataFrame(a).astype("float")

        detected_people = []
        for index, row in px.iterrows():
            x1, y1, x2, y2 = row

            class_name = "person"

            if 'person' in class_name:
                detected_people.append([int(x1), int(y1), int(x2), int(y2)])
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

        bbox_id = tracker.update(detected_people)

        people_in_rect_count = 0

        for bbox in bbox_id:
            x3, y3, x4, y4, person_id = bbox
            xt, yt = x4, y4

            if cv2.pointPolygonTest(np.array(area2, np.int32), (xt, yt), False) >= 0:
                entering.add(person_id)

            if person_id in entering:
                if cv2.pointPolygonTest(np.array(area1, np.int32), (xt, yt), False) >= 0:
                    exiting.add(person_id)

            if is_inside_rect([x3, y3, x4, y4], register_line_area):
                people_in_rect_count += 1

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

        # Log data every 10 frames
        if count % 10 == 0:
            log_entry = {
                "frame": count,
                "people_entered": num_entered,
                "people_exited": num_exited,
                "people_inside": num_inside,
                "estimated_waiting_time_seconds": int(avg_queue_length * TIME_PER_CUSTOMER)
            }
            log_data.append(log_entry)

        # Draw areas (polygons) for inside, outside, and register line
        cv2.polylines(frame, [np.array(area1, np.int32)], isClosed=True, color=(0, 255, 255), thickness=2)
        cv2.polylines(frame, [np.array(area2, np.int32)], isClosed=True, color=(255, 0, 0), thickness=2)
        cv2.rectangle(frame, tuple(register_line_area[0]), tuple(register_line_area[1]), (0, 0, 255), 2)

        if show_video:
            cv2.imshow("Frame", frame)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Write the log data to a JSON file after processing
    if LOG_PATH:
        with open(LOG_PATH, 'w') as log_file:
            json.dump(log_data, log_file, indent=4)  # Write the logs as JSON with indentation

    # Release the capture and close all windows
    cap.release()
    cv2.destroyAllWindows()
    return True
