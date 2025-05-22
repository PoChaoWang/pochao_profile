import os
import random
from confluent_kafka import SerializingProducer
import simplejson as json
from datetime import datetime, timedelta
import uuid
import time
import threading
from typing import Dict, Any
from math import sqrt, pow


TAIPEI_MAIN_STATION_COORDINATES = {"latitude": 25.0376, "longitude": 121.5569}
XINYI_SHOPPING_DISTRICT_COORDINATES = {"latitude": 25.0334, "longitude": 121.5643}
SHILIN_NIGHT_MARKET_COORDINATES = {"latitude": 25.0974, "longitude": 121.5245}
NEW_TAIPEI_CITY_HALL_COORDINATES = {"latitude": 25.0396, "longitude": 121.6547}
LINKOU_CHANG_GUNG_MEMORIAL_HOSPITAL_COORDINATES = {
    "latitude": 25.0692,
    "longitude": 121.3547,
}
SANCHONG_COORDINATES = {"latitude": 25.0726, "longitude": 121.4845}
BANQIAO_COORDINATES = {"latitude": 24.9953, "longitude": 121.4623}
XINZHUANG_COORDINATES = {"latitude": 25.0380, "longitude": 121.4325}
TAMSUI_OLD_STREET_COORDINATES = {"latitude": 25.1687, "longitude": 121.4474}
XIZHI_COORDINATES = {"latitude": 25.0647, "longitude": 121.6419}

# Store all coordinate points in a list
LOCATIONS = [
    TAIPEI_MAIN_STATION_COORDINATES,
    XINYI_SHOPPING_DISTRICT_COORDINATES,
    SHILIN_NIGHT_MARKET_COORDINATES,
    NEW_TAIPEI_CITY_HALL_COORDINATES,
    LINKOU_CHANG_GUNG_MEMORIAL_HOSPITAL_COORDINATES,
    SANCHONG_COORDINATES,
    BANQIAO_COORDINATES,
    XINZHUANG_COORDINATES,
    TAMSUI_OLD_STREET_COORDINATES,
    XIZHI_COORDINATES,
]


def get_random_start_end_locations():
    """Randomly select two different locations as start and end points"""
    start_location = random.choice(LOCATIONS)
    end_location = random.choice([loc for loc in LOCATIONS if loc != start_location])
    return start_location, end_location


def latitude_increment(coordinates_a, coordinates_b):
    return (coordinates_b["latitude"] - coordinates_a["latitude"]) / 100


def longitude_increment(coordinates_a, coordinates_b):
    return (coordinates_b["longitude"] - coordinates_a["longitude"]) / 100


# Environment Variables for configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
VEHICLE_TOPIC = os.getenv("VEHICLE_TOPIC", "vehicle_data")
GPS_TOPIC = os.getenv("GPS_TOPIC", "gps_data")
TRAFFIC_TOPIC = os.getenv("TRAFFIC_TOPIC", "traffic_data")
WEATHER_TOPIC = os.getenv("WEATHER_TOPIC", "weather_data")
DRIVER_TOPIC = os.getenv("DRIVER_TOPIC", "driver_data")
USER_TOPIC = os.getenv("USER_TOPIC", "user_data")
PAYMENT_TOPIC = os.getenv("PAYMENT_TOPIC", "payment_data")


random.seed(42)
start_time = datetime.now()

start_location, end_location = get_random_start_end_locations()
current_location = start_location.copy()

lat_increment = latitude_increment(current_location, end_location)
long_increment = longitude_increment(current_location, end_location)


def get_next_time():
    global start_time
    start_time += timedelta(seconds=random.randint(30, 60))
    return start_time


def generate_gps_data(device_id, timestamp, location):
    return {
        "gps_id": uuid.uuid4(),
        "deviceId": device_id,
        "latitude": location[0],
        "longitude": location[1],
        "speed": random.uniform(0, 40),  # km/h
        "timestamp": timestamp,
    }


def generate_traffic_data(device_id, timestamp, location):
    return {
        "traffic_id": uuid.uuid4(),
        "deviceId": device_id,
        "timestamp": timestamp,
        "latitude": location[0],
        "longitude": location[1],
        "status": random.choice(
            ["Clear", "Moderate", "Heavy", "Congested", "Standstill"]
        ),
    }


def generate_weather_data(device_id, timestamp, location):
    return {
        "driver_id": uuid.uuid4(),
        "deviceId": device_id,
        "timestamp": timestamp,
        "latitude": location[0],
        "longitude": location[1],
        "temperature": random.uniform(-5, 26),  # degrees Celsius
        "weatherCondition": random.choice(["Sunny", "Cloudy", "Rain", "Snow"]),
        "humidity": random.uniform(0, 100),  # percentage
        "windSpeed": random.uniform(0, 100),  # km/h
        "precipitation": random.uniform(0, 25),
        "airQualityIndex": random.uniform(0, 500),
    }


def generate_driver_data(device_id):
    return {
        "driver_id": uuid.uuid4(),
        "deviceId": device_id,
        "phone_number": "09" + str(random.randint(10000000, 99999999)),
        "name": random.choice(
            [
                "Smith",
                "Johnson",
                "Williams",
                "Brown",
                "Jones",
                "Garcia",
                "Miller",
                "Davis",
                "Rodriguez",
                "Martinez",
                "Anderson",
                "Taylor",
                "Thomas",
                "Moore",
                "Jackson",
                "Martin",
                "Lee",
                "Thompson",
                "White",
                "Harris",
            ]
        ),
        "email": f"driver{random.randint(100,999)}@{random.choice(['gmail.com', 'yahoo.com', 'hotmail.com'])}",
        "rating": round(random.uniform(3.5, 5.0), 1),
        "total_trips": random.randint(100, 5000),
        "years_experience": random.randint(1, 10),
        "license_number": "計程車駕駛執照-" + str(random.randint(10000, 99999)),
        "created_at": (
            datetime.now() - timedelta(days=random.randint(0, 365 * 6))
        ).isoformat(),
    }


def generate_user_data():
    return {
        "user_id": uuid.uuid4(),
        "phone_number": "09" + str(random.randint(10000000, 99999999)),
        "name": random.choice(
            [
                "Emma",
                "Michael",
                "Linda",
                "James",
                "David",
                "Susan",
                "Jason",
                "Helen",
                "Bruce",
                "Jenny",
                "Alice",
                "Robert",
                "Mary",
                "William",
                "Patricia",
                "John",
                "Jennifer",
                "Richard",
                "Barbara",
                "Thomas",
                "Daniel",
                "Sarah",
                "Joseph",
                "Elizabeth",
                "Charles",
                "Margaret",
                "Christopher",
                "Lisa",
                "Andrew",
                "Sandra",
            ]
        ),
        "email": f"user{random.randint(100,999)}@{random.choice(['gmail.com', 'yahoo.com', 'hotmail.com'])}",
        "rating": round(random.uniform(3.5, 5.0), 1),
        "total_trips": random.randint(1, 500),
        "created_at": (
            datetime.now() - timedelta(days=random.randint(0, 365 * 2))
        ).isoformat(),
    }


def generate_payment_data(trip_id, user_id, driver_id, distance, duration):
    base_fare = 70  # 起跳價
    per_km_rate = 25  # 每公里收費
    per_minute_rate = 2  # 每分鐘收費

    distance_fare = distance * per_km_rate
    time_fare = duration * per_minute_rate
    total_fare = base_fare + distance_fare + time_fare

    return {
        "payment_id": uuid.uuid4(),
        "trip_id": trip_id,
        "user_id": user_id,
        "driver_id": driver_id,
        "amount": round(total_fare, 2),
        "currency": "TWD",
        "payment_method": random.choice(["Credit Card", "Cash", "Mobile Payment"]),
        "status": "completed",
        "base_fare": base_fare,
        "distance_fare": round(distance_fare, 2),
        "time_fare": round(time_fare, 2),
        "timestamp": datetime.now().isoformat(),
    }


def calculate_distance(start_loc, end_loc):
    """Calculate approximate distance between two points (in kilometers)"""
    lat_diff = abs(end_loc["latitude"] - start_loc["latitude"])
    lon_diff = abs(end_loc["longitude"] - start_loc["longitude"])
    # Simplified distance calculation, should use more accurate geographic distance calculation in production
    return sqrt(pow(lat_diff * 111, 2) + pow(lon_diff * 111, 2))


def generate_vehicle_data(device_id, timestamp, location):
    return {
        "vehicle_id": uuid.uuid4(),
        "deviceId": device_id,
        "timestamp": timestamp,
        "latitude": location[0],
        "longitude": location[1],
        "speed": random.uniform(10, 40),
        "direction": random.choice(
            [
                "North",
                "South",
                "East",
                "West",
                "North-East",
                "North-West",
                "South-East",
                "South-West",
            ]
        ),
        "make": random.choice(["Toyota", "Honda", "Nissan", "Mitsubishi", "Lexus"]),
        "model": random.choice(["Altis", "Camry", "Civic", "Sentra", "Outlander"]),
        "year": random.randint(2018, 2024),
        "fuelType": random.choice(["Gasoline", "Hybrid", "Electric"]),
        "status": random.choice(["Available", "OnTrip", "Maintenance", "Offline"]),
    }


def simulate_vehicle_movement():
    global current_location, start_location, end_location, lat_increment, long_increment

    # Move towards target location
    current_location["latitude"] += lat_increment
    current_location["longitude"] += long_increment

    # Add some randomness to simulate actual road driving
    current_location["latitude"] += random.uniform(-0.0002, 0.0002)
    current_location["longitude"] += random.uniform(-0.0002, 0.0002)

    # Check if we need to choose a new destination
    if abs(current_location["latitude"] - end_location["latitude"]) < abs(
        lat_increment
    ) and abs(current_location["longitude"] - end_location["longitude"]) < abs(
        long_increment
    ):
        # Choose new start point (current location) and end point
        start_location = current_location.copy()
        end_location = random.choice(
            [loc for loc in LOCATIONS if loc != start_location]
        )
        lat_increment = latitude_increment(start_location, end_location)
        long_increment = longitude_increment(start_location, end_location)
        print(
            f"Arrived at destination, choosing new route: from {start_location} to {end_location}"
        )

    return current_location.copy()


def json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


def produce_data_to_kafka(producer, topic, data):
    id_field_map = {
        "vehicle_data": "vehicle_id",
        "gps_data": "gps_id",
        "traffic_data": "traffic_id",
        "weather_data": "driver_id",
        "driver_data": "driver_id",
        "user_data": "user_id",
        "payment_data": "payment_id",
    }

    id_field = id_field_map.get(topic, "id")

    producer.produce(
        topic,
        key=str(data[id_field]),
        value=json.dumps(data, default=json_serializer).encode("utf-8"),
        on_delivery=delivery_report,
    )
    producer.flush()


class TaxiSimulator:
    def __init__(self, device_id: str, producer: SerializingProducer = None):
        self.device_id = device_id
        self.producer = producer
        self.start_time = datetime.now()
        self.start_location, self.end_location = get_random_start_end_locations()
        self.current_location = self.start_location.copy()
        self.lat_increment = latitude_increment(
            self.current_location, self.end_location
        )
        self.long_increment = longitude_increment(
            self.current_location, self.end_location
        )
        self.journey_count = 0
        self.driver_data = generate_driver_data(device_id)
        self.current_trip_id = None
        self.current_user_data = None
        self.trip_start_time = None

    def get_next_time(self):
        """Get next timestamp"""
        self.start_time += timedelta(seconds=random.randint(30, 60))
        return self.start_time

    def start_new_trip(self):
        """Start a new trip"""
        self.current_trip_id = uuid.uuid4()
        self.current_user_data = generate_user_data()
        self.trip_start_time = datetime.now()

        if self.producer:
            produce_data_to_kafka(self.producer, DRIVER_TOPIC, self.driver_data)
            produce_data_to_kafka(self.producer, USER_TOPIC, self.current_user_data)

        # print(f"\n========== Vehicle {self.device_id} Starting New Trip ==========")
        # print(f"Trip ID: {self.current_trip_id}")
        # print("\n--- driver ---")
        # print(self.driver_data)
        # print("\n--- user ---")
        # print(self.current_user_data)
        # print("==============================================")

    def end_current_trip(self):
        """End current trip"""
        if self.current_trip_id and self.trip_start_time:
            trip_duration = (
                datetime.now() - self.trip_start_time
            ).total_seconds() / 60  # Convert to minutes
            distance = calculate_distance(self.start_location, self.end_location)
            payment_data = generate_payment_data(
                self.current_trip_id,
                self.current_user_data["user_id"],
                self.driver_data["driver_id"],
                distance,
                trip_duration,
            )

            if self.producer:
                produce_data_to_kafka(self.producer, PAYMENT_TOPIC, payment_data)

            # print(f"\n========== Vehicle {self.device_id} Trip End ==========")
            # print(f"Trip ID: {self.current_trip_id}")
            # print(f"Travel Distance: {distance:.2f} kilometers")
            # print(f"Travel Time: {trip_duration:.1f} minutes")
            # print("\n--- payment ---")
            # print(payment_data)
            # print("==============================================")

            self.current_trip_id = None
            self.current_user_data = None
            self.trip_start_time = None

    def simulate_movement(self):
        """Simulate vehicle movement"""
        # If no trip is in progress, start a new one
        if not self.current_trip_id:
            self.start_new_trip()

        # Move towards target location
        self.current_location["latitude"] += self.lat_increment
        self.current_location["longitude"] += self.long_increment

        # Add some randomness to simulate actual road travel
        self.current_location["latitude"] += random.uniform(-0.002, 0.002)
        self.current_location["longitude"] += random.uniform(-0.002, 0.002)

        # Check if destination is reached
        if abs(self.current_location["latitude"] - self.end_location["latitude"]) < abs(
            self.lat_increment
        ) and abs(
            self.current_location["longitude"] - self.end_location["longitude"]
        ) < abs(
            self.long_increment
        ):
            # End current trip
            self.end_current_trip()

            # Select new start point (current location) and end point
            self.start_location = self.current_location.copy()
            self.end_location = random.choice(
                [loc for loc in LOCATIONS if loc != self.start_location]
            )
            self.lat_increment = latitude_increment(
                self.start_location, self.end_location
            )
            self.long_increment = longitude_increment(
                self.start_location, self.end_location
            )

        return self.current_location.copy()


def simulate_single_taxi(
    producer: SerializingProducer, device_id: str, stop_event: threading.Event
):
    simulator = TaxiSimulator(device_id, producer)
    print(f"Starting simulation for vehicle {device_id}...")

    while not stop_event.is_set():
        try:
            current_time = simulator.get_next_time().isoformat()
            current_pos = simulator.simulate_movement()

            # Generate all data
            vehicle_data = generate_vehicle_data(
                device_id,
                current_time,
                (current_pos["latitude"], current_pos["longitude"]),
            )
            gps_data = generate_gps_data(
                device_id,
                current_time,
                (current_pos["latitude"], current_pos["longitude"]),
            )
            traffic_data = generate_traffic_data(
                device_id,
                current_time,
                (current_pos["latitude"], current_pos["longitude"]),
            )
            weather_data = generate_weather_data(
                device_id,
                current_time,
                (current_pos["latitude"], current_pos["longitude"]),
            )

            # Print data instead of sending to Kafka
            # print(f"\n========== Vehicle {device_id} Data Update ==========")
            # print(f"Timestamp: {current_time}")
            # print("\n--- Vehicle Data ---")
            # print(vehicle_data)

            # print("\n--- GPS Data ---")
            # print(gps_data)

            # print("\n--- Traffic Data ---")
            # print(traffic_data)

            # print("\n--- Weather Data ---")
            # print(weather_data)
            # print("==========================================")

            if producer:
                produce_data_to_kafka(producer, VEHICLE_TOPIC, vehicle_data)
                produce_data_to_kafka(producer, GPS_TOPIC, gps_data)
                produce_data_to_kafka(producer, TRAFFIC_TOPIC, traffic_data)
                produce_data_to_kafka(producer, WEATHER_TOPIC, weather_data)

            simulator.journey_count += 1

            # Set different update intervals for each vehicle to make trip times different
            time.sleep(random.uniform(3, 7))

        except Exception as e:
            print(f"Vehicle {device_id} data generation failed: {str(e)}")
            if not stop_event.is_set():
                time.sleep(5)  # Wait for a while before retrying after an error


def simulate_multiple_taxis(num_taxis: int = 5):
    producer_config = {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "error_cb": lambda err: print(f"Kafka error: {err}"),
    }
    producer = SerializingProducer(producer_config)

    # print("Starting Taipei Taxi Simulator...")
    # print(f"Number of simulated vehicles: {num_taxis}")
    # print("----------------------------------------")

    # Create stop event to control all threads
    stop_event = threading.Event()

    # Create and start simulation threads for all taxis
    threads = []
    for i in range(num_taxis):
        device_id = f"TPE-TAXI-{random.randint(1000, 9999)}"
        thread = threading.Thread(
            target=simulate_single_taxi,
            args=(
                producer,
                device_id,
                stop_event,
            ),  # Set producer back to the actual producer
        )
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Stagger vehicle start times


if __name__ == "__main__":
    try:
        simulate_multiple_taxis(5)

    except KeyboardInterrupt:
        print("Simulation ended by the user")
    except Exception as e:
        print(f"Unexpected Error occurred: {e}")
