import numpy as np
import queue

# Queue to manage charging stations
class ChargingStation:
    def __init__(self, num_ports):
        self.queue = queue.Queue(maxsize=num_ports)
        self.ports = num_ports
        self.charging_cars = 0
        self.charge_time = 0
        self.wait_time = 0
        self.wait_count = 0

    def queue_full(self):
        return self.queue.full()
    
    def queue_empty(self):
        return self.queue.empty()
    
    def chargers_free(self):
        return self.charging_cars < self.ports

    def add_car(self, car, time):
        if not self.queue.full():
            car.start_queue(time)
            self.queue.put_nowait(car)
            return True
        return False

    def start_charging(self, time):
        car = self.queue.get_nowait()
        wait_time = car.end_queue_get_wait(time)
        self.wait_count += 1
        self.wait_time += wait_time
        self.charging_cars += 1
        charge_time = round(np.random.normal(20, 5))
        self.charge_time += charge_time
        return charge_time, car
        
    def get_avg_wait_time(self):
        return self.wait_time/self.wait_count
    
    def car_leaves(self):
        if self.charging_cars > 0:
            self.charging_cars -= 1
    
    def get_util(self, simulation_time):
        return float(self.charge_time) / (simulation_time * self.ports)

class Car:
    def __init__(self, id):
        self.car_origin = id
        self.start_queue_time = None
        self.wait_time = None
    
    def start_queue(self, time):
        self.start_queue_time = time
    
    def end_queue_get_wait(self, time):
        self.wait_time = time - self.start_queue_time 
        return self.wait_time
    
    def get_origin(self):
        return self.car_origin

class Simulation:
    def __init__(self, df):
        self.data = self.pull_data(df)
        self.points = self.data['LHRS'].tolist()
        self.arrival_times = None
        self.stations = None
        self.station_ranges = None
        self.max_simulation_time = 120
        self.cars_charged = None
        self.cars_not_charged = None
    
    def pull_data(self, df):
        df['dist_to_next'] = (df['Sec Len'] + df['Sec Len'].shift(-1)) / 2
        df = df.astype({'AADT': int, 'LHRS': int,
                       'Latitude': float, 'Longitude': float})
        df['demand'] = df['AADT']*((1-(df['Truck %']/100))*0.033*0.02072)
        return df

    def setup(self, charging_stations, station_ranges):
        #Eventually random generate these based on demand
        self.arrival_times = { #use list.pop(0) to get the first one out 
            1: [10,20,30,40,50,60,70,80,90,100,110,120],
            2: [10,20,30,40,50,60,70,80,90,100,110,120],
            3: [10,20,30,40,50,60,70,80,90,100,110,120],
            4: [10,20,30,40,50,60,70,80,90,100,110,120],
            5: [10,20,30,40,50,60,70,80,90,100,110,120]
        }  # Vehicles arrive every X minutes
        self.station_ranges = station_ranges
        # Create Charging Stations
        self.stations = {
            station_id: ChargingStation(num_ports) for station_id, num_ports in charging_stations.items()
        }
        # Initialize outputs
        self.cars_charged = {point_id: 0 for point_id in self.points}
        self.cars_not_charged = {point_id: 0 for point_id in points}
        # self.wait_times = {station_id: [] for station_id in charging_stations.keys()}


    def get_closest_station(self, point_id, station_ranges):
        min_distance = None
        station = None
        for station_id, distance in iter(station_ranges[point_id].items()):
            if not min_distance or distance < min_distance:
                min_distance = distance
                station = station_id
        return station_id, min_distance

    def simulate(self, charging_stations, station_ranges):
        #Setup
        self.setup(charging_stations, station_ranges)
        station_arrivals = [] # Format = [[station_id, time, car]]
        station_departures = [] # Format = [[station_id, time]]
        #Run simulation
        for current_time in range(self.max_simulation_time):
            #Demand Generation Logic
            for point_id, arrive_list in self.arrival_times.items():
                if current_time == arrive_list[0]:  # Generate car at this point
                    arrive_list.pop(0) #remove arrival time
                    self.arrival_times.update({point_id:arrive_list})
                    car = Car(point_id) # Create car
                    if point_id in station_ranges:  # If within range of a station
                        station_id, distance = self.get_closest_station(point_id, station_ranges)
                        travel_time = distance / 100 * 60  # Time to station in minutes
                        station_arrivals.append([station_id, current_time + travel_time, car])
                        print(f"T{current_time}: Car appeared at {point_id}, driving for {travel_time} to {station_id}")
                    else:
                        self.cars_not_charged[point_id] += 1
                        print(f"T{current_time}: Car appeared at {point_id}, not in range")
            # Departure Logic #include charge counts
            for index, departure in enumerate(station_departures):
                if current_time == departure[1]:
                    station_id = departure[0]
                    self.stations[station_id].car_leaves()
                    print(f"T{current_time}: Car left station {station_id}")
                    if not self.stations[station_id].queue_empty():
                        charge_time, car = self.stations[station_id].start_charging(current_time)
                        station_departures.append([station_id, current_time + charge_time])
                        self.cars_charged[car.get_origin()] += 1
                        print(f"T{current_time}: Another car from {car.get_origin()} began charging at station {station_id} for {charge_time} minutes")
            # Station Arrival Logic
            for index, arrival in enumerate(station_arrivals):
                if current_time == arrival[1]:
                    station_id = arrival[0]
                    car = arrival[2]
                    if self.stations[station_id].add_car(car, current_time):
                        print(f"T{current_time}: Car from {car.get_origin()} arrived at station {station_id} and entered queue")
                        if self.stations[station_id].chargers_free():
                            charge_time, car = self.stations[station_id].start_charging(current_time)
                            station_departures.append([station_id, current_time + charge_time])
                            self.cars_charged[car.get_origin()] += 1
                            print(f"T{current_time}: Car from {car.get_origin()} began charging at station {station_id} for {charge_time} minutes")
                    else:
                        print(f"T{current_time}: Car from {car.get_origin()} arrived at station {station_id} and balked")
                        self.cars_not_charged[car.get_origin()] += 1
    
    def get_coverage(self):
        if not self.cars_charged:
            raise Exception("Simulation must have been run to get coverage!")
        coverage = {}
        for point_id, cars_charged in self.cars_charged.items():
            print(f"ID: {point_id}")
            print(f"Cars charged: {cars_charged}")
            print(f"Cars not charged: {self.cars_not_charged[point_id]}")
            coverage.update({
                point_id:round(float(cars_charged)/(self.cars_not_charged[point_id] + cars_charged),2)
            })
        return coverage
    
    def get_util(self):
        if not self.cars_charged:
            raise Exception("Simulation must have been run to get util!")
        util = {}
        for point_id, station in self.stations.items():
            util.update({point_id:round(station.get_util(self.max_simulation_time),2)})
        return util
    
    def get_wait_times(self):
        if not self.cars_charged:
            raise Exception("Simulation must have been run to get wait times!")
        wait_times = {}
        for point_id, station in self.stations.items():
            wait_times.update({point_id:round(station.get_avg_wait_time(),1)})
        return wait_times


if __name__ == '__main__':
    points = [1, 2, 3, 4, 5] #Testing will break on this, just set this to points in the Simulation init
    sim = Simulation(points)
    charging_stations = {2: 2, 5: 3}
    # Nearest charging station and distance
    station_ranges = {1: {2: 10, 5:5}, 2: {2: 0}, 3: {2: 5}, 5: {5:0} }
    sim.simulate(charging_stations, station_ranges)
    print(sim.get_coverage())
    print(sim.get_util())
    print(sim.get_wait_times())
