import cv2
import time
import threading
import queue
import logging
from datetime import datetime, timezone
import json
import numpy as np
from ultralytics import YOLO
import random

# import time # Already imported
from confluent_kafka import Producer
import uuid

# from datetime import datetime # Already imported
# from confluent_kafka import Producer # Already imported
from dotenv import load_dotenv
import os
import argparse  # For command-line arguments

load_dotenv()

# Logging setup
LOG_DIR = "../logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=os.path.join(LOG_DIR, "yolo.log"),
    filemode="a",
)

# Yolo model path and target classes
YOLO_MODEL_PATH = "yolov8s.pt"
TARGET_CLASSES = ["car", "truck", "bus"]
# OUTPUT_JSON_FILE is now determined inside yolo_processing_main based on location
CONFIDENCE_THRESHOLD = 0.25
# For YOLO model input size
IMGASZ = 320

MIN_SPEED_CALC_TIME_SECONDS = 0.1
MAX_SPEED_CALC_TIME_SECONDS = 10.0

# Speed zone configuration file path
CONFIG_FILE_PATH = "speed_zones_config.json"

# Frame buffer and running state remain global
FRAME_BUFFER_SIZE = 3
frame_buffer = queue.Queue(maxsize=FRAME_BUFFER_SIZE)
is_running = True  # Global flag to control threads

# Kafka Producer setup (remains mostly the same)
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "127.0.0.1:9092")
KAFKA_PRODUCER_CONFIG = {
    "bootstrap.servers": KAFKA_BROKER,
    "queue.buffering.max.messages": 10000,
    "queue.buffering.max.ms": 20,
}
kafka_producer = None  # Initialize to None
try:
    kafka_producer = Producer(KAFKA_PRODUCER_CONFIG)
    logging.info(f"Kafka Producer initialized with broker: {KAFKA_BROKER}")
except Exception as e:
    logging.error(f"Kafka Producer initialization failed: {e}")
    # producer = None # kafka_producer is already None if this fails
kafka_topic = os.getenv("KAFKA_TOPIC", "yolo_detections_topic")


# Assistant Function
# Function to get a fresh video URL
def get_fresh_video_url(base_url):
    t_param = random.random()
    return f"{base_url}&t={t_param}"


# Function to calculate the midpoint of two points
def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)


def get_point_side_val(line_p1, line_p2, point):
    return (line_p2[0] - line_p1[0]) * (point[1] - line_p1[1]) - (
        line_p2[1] - line_p1[1]
    ) * (point[0] - line_p1[0])


class FrameInfo:
    def __init__(self, frame, capture_time_utc, frame_source_url):
        self.frame = frame
        self.capture_time_utc = capture_time_utc
        self.frame_source_url = frame_source_url


# Get the video frame from the camera and make sure it keeps running
class CaptureThread(threading.Thread):
    def __init__(
        self, base_url, thread_name="CCTV-CaptureThread"
    ):  # base_url is now passed
        super().__init__(name=thread_name)
        self.base_url = base_url
        self.current_url = ""
        self.cap = None
        self.daemon = True  # Ensure thread exits when main program exits

    # Handle video stream capture
    def run(self):
        global is_running, frame_buffer
        logging.info(f"Capture thread started, target base URL: {self.base_url}")
        max_connect_retries = 5
        connect_retry_delay_base = 2

        while is_running:
            connected = False
            if not self.base_url:  # Safety check if base_url wasn't provided
                logging.error("Capture thread started without a valid base URL.")
                break
            for attempt in range(max_connect_retries):
                if not is_running:
                    break
                try:
                    self.current_url = get_fresh_video_url(self.base_url)
                    self.cap = cv2.VideoCapture(self.current_url)
                    if not self.cap.isOpened():
                        raise ConnectionError(f"Connection error: {self.current_url}")
                    self.cap.set(
                        cv2.CAP_PROP_BUFFERSIZE, 1
                    )  # Try to get the latest frame
                    logging.info(f"Connected to: {self.current_url}")
                    connected = True
                    break
                except Exception as e:
                    logging.error(
                        f"Connection error (Try {attempt + 1}/{max_connect_retries}): {e}"
                    )
                    if self.cap:
                        self.cap.release()
                    time.sleep(
                        connect_retry_delay_base * (2**attempt)
                    )  # Exponential backoff

            if not connected:
                logging.error(
                    f"Failed to establish video stream connection to {self.base_url}. Thread will wait longer before retrying."
                )
                time.sleep(
                    30
                )  # Wait longer before retrying the whole connection process
                continue

            while is_running and self.cap and self.cap.isOpened():
                try:
                    capture_time_utc = datetime.now(timezone.utc)
                    ret, frame = self.cap.read()
                    if not ret:
                        logging.warning(
                            f"Failed to read frame from {self.current_url}. The video stream may have been interrupted."
                        )
                        break  # Break inner loop to attempt reconnection
                    if frame is None:
                        logging.warning(
                            f"Received an empty frame from {self.current_url}."
                        )
                        time.sleep(0.1)  # Short pause before trying again
                        continue

                    if frame_buffer.full():
                        try:
                            frame_buffer.get_nowait()  # Discard oldest frame
                        except queue.Empty:
                            pass  # Should not happen if full() is true
                    frame_info = FrameInfo(
                        frame.copy(), capture_time_utc, self.current_url
                    )
                    frame_buffer.put(frame_info)
                    # time.sleep(0.01) # Small delay to prevent overwhelming CPU if stream is too fast, adjust as needed
                except cv2.error as e:
                    logging.error(f"OpenCV Error: {e}", exc_info=True)
                    break  # Break inner loop
                except Exception as e:
                    logging.error(
                        f"Unexpected error occurred during capture: {e}", exc_info=True
                    )
                    break  # Break inner loop

            if self.cap:
                self.cap.release()
                self.cap = None

            if not is_running:  # Check flag before sleeping
                break

            logging.info(
                f"Video stream {self.current_url} interrupted or finished, preparing to reconnect."
            )
            time.sleep(0.5)  # Brief pause before attempting to reconnect

        if self.cap:  # Ensure release if loop broken while cap is active
            self.cap.release()
        logging.info("Capture thread stopped.")


# Loads speed zone configurations from a JSON file and returns the base video URL and speed zones.
def load_location_configuration(config_path, location_name):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            all_configs = json.load(f)

        location_config = all_configs[location_name]
        base_video_url = location_config.get("BASE_VIDEO_URL")
        speed_zones_raw = location_config.get("SPEED_ZONES", [])

        # Convert lists from JSON to tuples as expected by OpenCV and other parts of the code
        processed_speed_zones = []
        for zone in speed_zones_raw:
            try:
                zone["line1_points"] = tuple(map(tuple, zone["line1_points"]))
                zone["line2_points"] = tuple(map(tuple, zone["line2_points"]))
                zone["line1_color"] = tuple(zone["line1_color"])
                zone["line2_color"] = tuple(zone["line2_color"])
                processed_speed_zones.append(zone)
            except KeyError as e:
                logging.error(
                    f"Zone '{zone.get('name', 'Unnamed Zone')}' configuration is incomplete (missing {e}), skipping this zone."
                )
            except Exception as e_zone:
                logging.error(
                    f"Error processing zone '{zone.get('name', 'Unnamed Zone')}' configuration: {e_zone}, skipping this zone."
                )

        return base_video_url, processed_speed_zones

    except FileNotFoundError:
        logging.error(f"'{config_path}' does not exist.")
        return None, None
    except json.JSONDecodeError:
        logging.error(f"'{config_path}' file is not a valid JSON.")
        return None, None
    except Exception as e:
        logging.error(
            f"An unexpected error occurred while loading the config file '{config_path}': {e}"
        )
        return None, None


# Modified yolo_processing_main
def yolo_processing_main(location_name: str):
    global is_running, frame_buffer, kafka_producer, kafka_topic  # is_running and frame_buffer are global

    # Load configuration for the specified location
    BASE_VIDEO_URL, SPEED_ZONES = load_location_configuration(
        CONFIG_FILE_PATH, location_name
    )

    if (
        not BASE_VIDEO_URL or SPEED_ZONES is None
    ):  # SPEED_ZONES can be an empty list if configured that way
        logging.error(
            f"Failed to load a valid configuration for location '{location_name}'. The program will terminate."
        )
        is_running = False  # Ensure other threads know to stop
        return []

    if not SPEED_ZONES:
        logging.warning(
            f"No speed zones (SPEED_ZONES) defined for location '{location_name}'. Only object detection will be performed."
        )

    # --- Dynamic Output JSON File Name ---
    current_date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_json_dir = "./yolo_json"
    task_code = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=4))
    task_number = random.randint(100, 999)
    os.makedirs(output_json_dir, exist_ok=True)  # Ensure directory exists
    OUTPUT_JSON_FILE = f"{output_json_dir}/{current_date_time_str}_{location_name}_{task_code}_{task_number}.json"
    logging.info(f"Output JSON file: {OUTPUT_JSON_FILE}")

    logging.info(f"Starting YOLO processing for location: {location_name}")
    logging.info(f"Video URL: {BASE_VIDEO_URL}")
    logging.info(
        f"Yolo Model: {YOLO_MODEL_PATH}, Size: {IMGASZ}, Confidence: {CONFIDENCE_THRESHOLD}"
    )
    logging.info("Press 'q' to close the video window and exit the program.")

    # Pre-calculate zone boundary sense for the loaded SPEED_ZONES
    for zone in SPEED_ZONES:
        l1p1, l1p2 = zone["line1_points"]
        l2p1, l2p2 = zone["line2_points"]
        m_l1 = midpoint(l1p1, l1p2)
        m_l2 = midpoint(l2p1, l2p2)
        val_m2_wrt_l1 = get_point_side_val(l1p1, l1p2, m_l2)
        val_m1_wrt_l2 = get_point_side_val(l2p1, l2p2, m_l1)

        if val_m2_wrt_l1 == 0 or val_m1_wrt_l2 == 0:
            logging.warning(
                f"Zone '{zone['name']}' lines may be collinear or intersecting in a way "
                f"that makes 'between' ambiguous. Region detection might be unreliable."
            )
            zone["l1_inside_sign"] = 0
            zone["l2_inside_sign"] = 0
        else:
            zone["l1_inside_sign"] = np.sign(val_m2_wrt_l1)
            zone["l2_inside_sign"] = np.sign(val_m1_wrt_l2)
        logging.info(
            f"Zone '{zone['name']}' L1 inside sign: {zone['l1_inside_sign']}, L2 inside sign: {zone['l2_inside_sign']}"
        )

    # This function now correctly uses the pre-calculated signs
    def is_point_in_zone(point, zone_config):
        l1p1, l1p2 = zone_config["line1_points"]
        l2p1, l2p2 = zone_config["line2_points"]

        if zone_config["l1_inside_sign"] == 0 or zone_config["l2_inside_sign"] == 0:
            return False

        val_pt_wrt_l1 = get_point_side_val(l1p1, l1p2, point)
        val_pt_wrt_l2 = get_point_side_val(l2p1, l2p2, point)

        on_inside_of_l1 = (np.sign(val_pt_wrt_l1) == zone_config["l1_inside_sign"]) or (
            val_pt_wrt_l1 == 0
        )
        on_inside_of_l2 = (np.sign(val_pt_wrt_l2) == zone_config["l2_inside_sign"]) or (
            val_pt_wrt_l2 == 0
        )

        return on_inside_of_l1 and on_inside_of_l2

    try:
        model = YOLO(YOLO_MODEL_PATH)
        logging.info(f"Loaded Successfully '{YOLO_MODEL_PATH}'")
    except Exception as e:
        logging.error(f"Unable to load YOLO model: {e}", exc_info=True)
        is_running = False
        return []

    tracked_objects = {}
    output_data_list = []

    # Pass the loaded BASE_VIDEO_URL to CaptureThread
    capture_thread = CaptureThread(
        BASE_VIDEO_URL, thread_name=f"{location_name}-CaptureThread"
    )
    capture_thread.start()

    frames_processed_count = 0
    fps_calc_start_time = time.monotonic()
    displayed_processing_fps = 0.0

    # Main processing loop
    try:
        while is_running:
            try:
                frame_info = frame_buffer.get(timeout=1.0)  # Increased timeout slightly
            except queue.Empty:
                if not capture_thread.is_alive() and is_running:
                    logging.error(
                        f"Capture thread ({location_name}-CaptureThread) has stopped! Attempting to restart..."
                    )
                    # Ensure old thread is properly finished if possible (though daemon should handle it)
                    if capture_thread.is_alive():
                        capture_thread.join(timeout=1.0)  # Defensive
                    capture_thread = CaptureThread(
                        BASE_VIDEO_URL,
                        thread_name=f"{location_name}-CaptureThread-Restart",
                    )
                    capture_thread.start()
                elif not is_running:  # Check if main loop should terminate
                    break
                continue  # Continue if queue is empty but thread is alive

            frame = frame_info.frame
            current_capture_time_utc = frame_info.capture_time_utc

            frames_processed_count += 1
            current_monotonic_time_for_fps = time.monotonic()
            if current_monotonic_time_for_fps - fps_calc_start_time >= 1.0:
                time_elapsed_for_fps = (
                    current_monotonic_time_for_fps - fps_calc_start_time
                )
                displayed_processing_fps = (
                    frames_processed_count / time_elapsed_for_fps
                    if time_elapsed_for_fps > 0
                    else frames_processed_count
                )
                # logging.info(f"實際YOLO+追蹤處理 FPS: {displayed_processing_fps:.2f}") # Logged too frequently
                frames_processed_count = 0
                fps_calc_start_time = current_monotonic_time_for_fps

            results = model.track(
                frame,
                persist=True,
                verbose=False,
                classes=[
                    i
                    for i, cls_name in model.names.items()
                    if cls_name in TARGET_CLASSES
                ],
                conf=CONFIDENCE_THRESHOLD,
                tracker="bytetrack.yaml",
                imgsz=IMGASZ,
            )

            detections_for_json_current_frame = []
            current_track_ids_in_frame = set()

            if (
                results
                and results[0].boxes is not None
                and results[0].boxes.id is not None
            ):
                boxes_xyxy = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.cpu().numpy().astype(int)
                current_track_ids_in_frame.update(
                    track_ids
                )  # Keep track of IDs seen in this frame

                for i, track_id in enumerate(track_ids):
                    x1, y1, x2, y2 = boxes_xyxy[i]
                    confidence = results[0].boxes.conf.cpu().numpy()[i]
                    class_id = int(results[0].boxes.cls.cpu().numpy()[i])
                    class_name = model.names[class_id]
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    current_center_point = (center_x, center_y)

                    current_frame_speed_kmh_display = 0.0

                    if track_id not in tracked_objects:
                        tracked_objects[track_id] = {
                            "last_seen_utc": current_capture_time_utc,
                            "class_name": class_name,
                            "disappeared_counter": 0,  # Reset disappeared counter
                            "speeds_in_zones": {
                                zone["name"]: {
                                    "is_object_currently_in_zone": False,
                                    "zone_entry_timestamp_utc": None,
                                    "speed_kmh": 0.0,
                                    "last_calc_entry_time_iso": None,
                                    "last_calc_exit_time_iso": None,
                                }
                                for zone in SPEED_ZONES  # Initialize for all configured zones
                            },
                        }
                    else:
                        tracked_objects[track_id][
                            "last_seen_utc"
                        ] = current_capture_time_utc
                        tracked_objects[track_id][
                            "class_name"
                        ] = class_name  # Update class name if tracker changed it
                        tracked_objects[track_id]["disappeared_counter"] = 0

                    object_data = tracked_objects[track_id]

                    # Iterate through SPEED_ZONES (which are now specific to the location)
                    for zone_config in SPEED_ZONES:
                        zone_name = zone_config["name"]
                        zone_state = object_data["speeds_in_zones"][zone_name]
                        real_length = zone_config["real_length_meters"]

                        point_is_now_inside_zone = is_point_in_zone(
                            current_center_point, zone_config
                        )
                        was_object_in_zone_previously = zone_state[
                            "is_object_currently_in_zone"
                        ]

                        if (
                            point_is_now_inside_zone
                            and not was_object_in_zone_previously
                        ):
                            zone_state["zone_entry_timestamp_utc"] = (
                                current_capture_time_utc
                            )
                            zone_state["speed_kmh"] = 0.0  # Reset speed for new transit
                            zone_state["last_calc_entry_time_iso"] = None
                            zone_state["last_calc_exit_time_iso"] = None
                            logging.debug(
                                f"Object {track_id} ({class_name}) entered Zone '{zone_name}' @ {current_capture_time_utc.isoformat()}"
                            )

                        elif (
                            not point_is_now_inside_zone
                            and was_object_in_zone_previously
                        ):
                            logging.debug(
                                f"Object {track_id} ({class_name}) leaved Zone '{zone_name}' @ {current_capture_time_utc.isoformat()}"
                            )
                            if zone_state["zone_entry_timestamp_utc"] is not None:
                                time_in_zone_seconds = (
                                    current_capture_time_utc
                                    - zone_state["zone_entry_timestamp_utc"]
                                ).total_seconds()

                                if (
                                    MIN_SPEED_CALC_TIME_SECONDS
                                    < time_in_zone_seconds
                                    < MAX_SPEED_CALC_TIME_SECONDS
                                ):
                                    speed_mps = real_length / time_in_zone_seconds
                                    calculated_speed_kmh = round(speed_mps * 3.6, 1)
                                    zone_state["speed_kmh"] = calculated_speed_kmh
                                    current_frame_speed_kmh_display = (
                                        calculated_speed_kmh  # For immediate display
                                    )
                                    zone_state["last_calc_entry_time_iso"] = zone_state[
                                        "zone_entry_timestamp_utc"
                                    ].isoformat()
                                    zone_state["last_calc_exit_time_iso"] = (
                                        current_capture_time_utc.isoformat()
                                    )
                                    logging.info(
                                        f"Object {track_id} Speed ({zone_name}): {calculated_speed_kmh:.1f} km/h. "
                                        f"Entrance: {zone_state['last_calc_entry_time_iso']}, "
                                        f"Leave: {zone_state['last_calc_exit_time_iso']} ({time_in_zone_seconds:.2f}s)"
                                    )
                                else:
                                    logging.warning(
                                        f"Object {track_id} ({zone_name}) spent an unreasonable amount of time in the zone: {time_in_zone_seconds:.2f}s. Speed not calculated."
                                    )
                                zone_state["zone_entry_timestamp_utc"] = (
                                    None  # Reset for next transit
                                )
                            else:
                                logging.warning(
                                    f"Object {track_id} ({zone_name}) left the zone but has no entry timestamp."
                                )

                        zone_state["is_object_currently_in_zone"] = (
                            point_is_now_inside_zone
                        )

                        if (
                            zone_state["is_object_currently_in_zone"]
                            and zone_state["zone_entry_timestamp_utc"]
                        ):
                            duration_so_far = (
                                current_capture_time_utc
                                - zone_state["zone_entry_timestamp_utc"]
                            ).total_seconds()
                            if duration_so_far > MAX_SPEED_CALC_TIME_SECONDS:
                                logging.info(
                                    f"Object {track_id} stayed in zone '{zone_name}' for more than {MAX_SPEED_CALC_TIME_SECONDS}s. Resetting entry time for next detection."
                                )
                                zone_state["zone_entry_timestamp_utc"] = None

                    # Prepare JSON data (outside zone loop, but uses data from all zones)
                    detection_info_for_json = {
                        "capture_date_utc": current_capture_time_utc.strftime(
                            "%Y-%m-%d"
                        ),
                        "capture_time_utc": current_capture_time_utc.strftime(
                            "%H:%M:%S.%f"
                        )[
                            :-3
                        ],  # Milliseconds
                        "object_id": f"{task_code}_{task_number}_{location_name}_{track_id}",  # Include location in ID
                        "uuid": str(uuid.uuid4()),
                        "class": class_name,
                        "bounding_box_x1": float(x1),
                        "bounding_box_y1": float(y1),
                        "bounding_box_x2": float(x2),
                        "bounding_box_y2": float(y2),
                        "confidence": float(confidence),
                        "center_pixels_x": float(center_x),
                        "center_pixels_y": float(center_y),
                        "location_name": location_name,  # Add location name to the record
                        "frame_source_url": frame_info.frame_source_url,  # Add frame source
                        "zones_data": [],  # Store data for each zone
                    }
                    # Populate zone-specific data
                    for (
                        zone_config_json
                    ) in SPEED_ZONES:  # Ensure all zones are in json for this object
                        zone_n = zone_config_json["name"]
                        zs = object_data["speeds_in_zones"][zone_n]
                        detection_info_for_json[f"zone_name"] = (
                            zone_n  # Explicitly name for multi-zone
                        )
                        detection_info_for_json[f"speed_kmh"] = zs["speed_kmh"]

                    detections_for_json_current_frame.append(detection_info_for_json)

                    # --- Send data to Kafka ---
                    if kafka_producer:  # Check if producer is available
                        produce_data_to_kafka(
                            kafka_producer, kafka_topic, detection_info_for_json
                        )
                    else:
                        logging.debug(
                            "Kafka producer not available, skipping message send."
                        )

                    # --- Drawing ---
                    display_label = f"ID:{track_id} {class_name} {confidence:.2f}"
                    cv2.rectangle(
                        frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2
                    )
                    cv2.putText(
                        frame,
                        display_label,
                        (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 255, 0),
                        1,
                    )

                    active_zone_speed_text = ""
                    if (
                        current_frame_speed_kmh_display > 0
                    ):  # Speed just calculated this frame
                        active_zone_speed_text = (
                            f"{current_frame_speed_kmh_display:.1f}km/h"
                        )
                    else:  # Check for previously calculated speeds if object is still in a zone or recently exited
                        for zn_cfg_draw in SPEED_ZONES:
                            zn_state_draw = object_data["speeds_in_zones"][
                                zn_cfg_draw["name"]
                            ]
                            if (
                                zn_state_draw["is_object_currently_in_zone"]
                                and zn_state_draw["speed_kmh"] > 0
                            ):
                                active_zone_speed_text = f"{zn_state_draw['speed_kmh']:.1f}km/h (in {zn_cfg_draw['name'][:5]}..)"
                                break
                            elif (
                                zn_state_draw["speed_kmh"] > 0
                                and zn_state_draw["last_calc_exit_time_iso"]
                            ):
                                try:
                                    exit_dt = datetime.fromisoformat(
                                        zn_state_draw["last_calc_exit_time_iso"]
                                    )
                                    if (
                                        current_capture_time_utc - exit_dt
                                    ).total_seconds() < 2.0:  # Show for 2s after exit
                                        active_zone_speed_text = f"{zn_state_draw['speed_kmh']:.1f}km/h ({zn_cfg_draw['name'][:5]}..)"
                                        break
                                except (
                                    ValueError
                                ):  # Handle cases where fromisoformat might fail if string is malformed
                                    pass

                    if active_zone_speed_text:
                        cv2.putText(
                            frame,
                            active_zone_speed_text,
                            (int(x1), int(y2) + 15),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (255, 0, 255),
                            2,
                        )

            # --- Post-detection processing for the frame ---
            cv2.putText(
                frame,
                f"FPS: {displayed_processing_fps:.2f} Loc: {location_name}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                frame,
                f"Time: {datetime.now().strftime('%H:%M:%S')}",
                (frame.shape[1] - 150, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )

            # --- Tracked Object Maintenance ---
            # Increment disappeared counter for objects not in current_track_ids_in_frame
            # and remove very old ones
            inactive_time_threshold_seconds = 10.0  # Increased threshold slightly
            ids_to_remove_from_tracked = []
            for tid, data in list(
                tracked_objects.items()
            ):  # Use list() for safe iteration while modifying
                if tid not in current_track_ids_in_frame:
                    data[
                        "disappeared_counter"
                    ] += 1  # This counter isn't strictly used in current logic but good for debugging
                    time_since_last_seen = (
                        current_capture_time_utc - data["last_seen_utc"]
                    ).total_seconds()
                    if time_since_last_seen > inactive_time_threshold_seconds:
                        ids_to_remove_from_tracked.append(tid)
                else:  # Reset counter if seen
                    data["disappeared_counter"] = 0

            for tid_to_remove in ids_to_remove_from_tracked:
                if tid_to_remove in tracked_objects:
                    logging.debug(
                        f"Removing inactive object ID: {tid_to_remove} for location {location_name}"
                    )
                    del tracked_objects[tid_to_remove]

            # --- Draw speed zones on the frame ---
            for zone in SPEED_ZONES:
                cv2.line(
                    frame,
                    zone["line1_points"][0],
                    zone["line1_points"][1],
                    zone["line1_color"],
                    2,
                )
                cv2.line(
                    frame,
                    zone["line2_points"][0],
                    zone["line2_points"][1],
                    zone["line2_color"],
                    2,
                )
                # Optionally, put zone name
                # cv2.putText(frame, zone["name"], (zone["line1_points"][0][0], zone["line1_points"][0][1] - 5),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

            cv2.imshow(f"YOLOv8 Zonal Speed Detection - {location_name}", frame)

            if detections_for_json_current_frame:
                output_data_list.extend(detections_for_json_current_frame)

            if len(output_data_list) > 2000:  # Prune older data
                output_data_list = output_data_list[-1000:]  # Keep last 1000

            # Save to JSON periodically or on change (optional, consider performance)
            # For now, saving is done at the end. Can be moved here if needed.

            if cv2.waitKey(1) & 0xFF == ord("q"):
                logging.info("User pressed 'q' key, preparing to exit the program.")
                is_running = False  # Set global flag
                break

    except KeyboardInterrupt:
        logging.info(
            "User interruption detected (Ctrl+C), preparing to exit the program."
        )
        is_running = False  # Set global flag
    except Exception as e_main_loop:
        logging.error(
            f"Unexpected error occurred in main processing loop ({location_name}): {e_main_loop}",
            exc_info=True,
        )
        is_running = False  # Set global flag
    finally:
        logging.info(f"YOLO main processing ({location_name}) is shutting down...")
        is_running = False  # Ensure flag is set for other threads

        if capture_thread and capture_thread.is_alive():
            logging.info(
                f"Waiting for capture thread ({capture_thread.name}) to finish..."
            )
            capture_thread.join(timeout=5.0)
            if capture_thread.is_alive():
                logging.warning(
                    f"Capture thread ({capture_thread.name}) did not finish within the timeout."
                )

        cv2.destroyAllWindows()  # Close OpenCV windows

        if kafka_producer:
            logging.info("Flushing Kafka producer buffer...")
            kafka_producer.flush(timeout=10)  # Wait up to 10 seconds
            logging.info("Kafka producer buffer has been flushed.")

        try:
            # Ensure directory exists for final save
            os.makedirs(os.path.dirname(OUTPUT_JSON_FILE), exist_ok=True)
            with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f_json_final:
                # Add default=json_serializer to this call as well
                json.dump(
                    output_data_list,
                    f_json_final,
                    indent=2,
                    ensure_ascii=False,
                    default=json_serializer,
                )
            logging.info(f"Results have been saved to {OUTPUT_JSON_FILE}")
        except Exception as e_json_final_write:
            logging.error(
                f"An error occurred while writing the final JSON file '{OUTPUT_JSON_FILE}': {e_json_final_write}",
                exc_info=True,
            )

        logging.info(f"YOLO main processing ({location_name}) has been shut down.")

    return output_data_list


def json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):  # Handles datetime.datetime objects
        return obj.isoformat()
    if isinstance(obj, np.bool_):  # Handles numpy.bool_
        return bool(obj)  # Convert to Python's native bool
    if isinstance(obj, np.integer):  # Handles numpy's integer types (e.g., np.int64)
        return int(obj)  # Convert to Python's native int
    if isinstance(obj, np.floating):  # Handles numpy's float types (e.g., np.float64)
        return float(obj)  # Convert to Python's native float
    if isinstance(obj, np.ndarray):  # Handles numpy arrays
        return obj.tolist()

    # If json.dumps somehow passed a standard Python type that it should have handled,
    # let it pass through. This is a fallback.
    if isinstance(obj, (bool, int, float, str, list, dict)) or obj is None:
        return obj

    # If we reach here, it's a type we haven't explicitly handled.
    raise TypeError(
        f"Type {obj.__class__.__name__} (Python type: {type(obj)}) is not JSON serializable by custom_serializer"
    )


def delivery_report(err, msg):
    if err is not None:
        logging.error(f"Message delivery failed ({msg.key()}): {err}")
    else:
        logging.debug(  # Changed to debug to reduce log verbosity
            f"Message successfully delivered to topic '{msg.topic()}' partition [{msg.partition()}] @ offset {msg.offset()} (Key: {msg.key()})"
        )


def produce_data_to_kafka(producer, topic, data_dict):
    # The original log message "啟動 YOLO 處理並即時將結果發送到 Kafka" is better suited for main execution start
    # This function is called per detection.
    if not producer:
        logging.warning("Kafka producer is None, cannot send message.")
        return

    try:
        # Ensure data_dict is a dictionary before accessing "uuid" or serializing
        if not isinstance(data_dict, dict):
            logging.error(
                f"Attempted to send non-dict data to Kafka: {type(data_dict)}"
            )
            return

        message_key = str(
            data_dict.get("uuid", str(uuid.uuid4()))
        )  # Fallback key if uuid missing
        message_value = json.dumps(data_dict, default=json_serializer).encode("utf-8")

        producer.produce(
            topic,
            key=message_key,
            value=message_value,
            callback=delivery_report,  # Use callback instead of on_delivery
        )

        producer.poll(0)  # Non-blocking poll to trigger callbacks and internal events.

    except BufferError as e:  # This error means producer's local queue is full.
        logging.error(f"Kafka Producer 內部佇列已滿: {e}. 訊息可能遺失。")

    except Exception as e:
        logging.error(
            f"An unexpected error occurred while sending message to Kafka topic '{topic}': {e}",
            exc_info=True,
        )


if __name__ == "__main__":
    # --- PyTorch/CUDA 檢查 ---
    try:
        import torch

        logging.info(f"PyTorch version: {torch.__version__}")
        logging.info(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            logging.info(f"CUDA device count: {torch.cuda.device_count()}")
            logging.info(f"Current CUDA device: {torch.cuda.current_device()}")
            logging.info(
                f"Device name: {torch.cuda.get_device_name(torch.cuda.current_device())}"
            )
        else:
            logging.warning("CUDA is NOT available. YOLO will run on CPU.")
    except ImportError:
        logging.warning("PyTorch not installed. Cannot check CUDA status.")
    except Exception as e_torch:
        logging.error(f"Error checking PyTorch/CUDA: {e_torch}")

    # Linkou = "Linkou"
    Zonghe = "Zonghe"  # 或者選擇 "Linkou"

    try:
        yolo_processing_main(Zonghe)
    except Exception as e_global:
        logging.critical(
            f"Unhandled top-level error caused program termination: {e_global}",
            exc_info=True,
        )
    finally:
        logging.info("Program execution finished.")
        if kafka_producer:
            logging.info("Performing final Kafka Producer flush...")
            kafka_producer.flush(timeout=10)
