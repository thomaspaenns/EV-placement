import numpy as np
import queue

# Methods to manage charging stations


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
        if self.wait_count == 0:
            return -1
        else:
            return round(self.wait_time/self.wait_count, 1)

    def car_leaves(self):
        if self.charging_cars > 0:
            self.charging_cars -= 1

    def get_util(self, simulation_time):
        util = float(self.charge_time) / (simulation_time * self.ports)
        if util > 1.000:
            util = 1.000
        return util

# Methods to track car movements


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
    # Initialize all the simulation parameters
    def __init__(self, df):
        self.data = self.pull_data(df)
        # [1, 2, 3, 4, 5] # for testing
        self.points = self.data['LHRS'].tolist()
        self.stations = None
        self.station_ranges = None
        self.max_simulation_time = 1440
        self.cars_charged = None
        self.cars_not_charged = None
        self.arrival_times = {}
        # for index, row in self.data.iterrows():
        #     inter_time = (24*60)/row['demand']
        #     beta = inter_time # 0
        #     # This is an adjustor - un-comment to artifically increase rural demand
        #     # if inter_time > 100.0:
        #     #     beta = inter_time/2
        #     # elif inter_time > 40.0:
        #     #     beta = inter_time/1.5
        #     # else:
        #     #     beta = inter_time
        #     time = 0
        #     arrivals = []
        #     while time < self.max_simulation_time:
        #         time = time + round(np.random.exponential(beta))
        #         arrivals.append(time)
        #     self.arrival_times.update({row['LHRS']:arrivals})

    # Format the dataframe
    def pull_data(self, df):
        df['dist_to_next'] = (df['Sec Len'] + df['Sec Len'].shift(-1)) / 2
        df = df.astype({'AADT': int, 'LHRS': int,
                       'Latitude': float, 'Longitude': float})
        df['demand'] = df['AADT']*((1-(df['Truck %']/100))*0.033*0.02072)
        return df

    # Create specific stations for this simulation
    def setup(self, charging_stations, station_ranges, year=2024):
        year_convert = {2024:1.0, 2029: 4.12, 2034:7.24, 2039:10.36, 2044:13.48, 2049: 16.6}
        # year_convert = {2024:1.0, 2029: 4.12, 2034:9.24, 2039:13.36, 2044:17.48, 2049: 21.6} #75%
        yr_scalar = year_convert[year]
        self.cars_charged = None
        self.cars_not_charged = None
        self.arrival_times = {}
        for index, row in self.data.iterrows():
            inter_time = (24*60)/(row['demand']*yr_scalar)
            beta = inter_time  # 0
            # print(f"BETA: {beta}")
            # This is an adjustor - un-comment to artifically increase rural demand
            # if inter_time > 100.0:
            #     beta = inter_time/2
            # elif inter_time > 40.0:
            #     beta = inter_time/1.5
            # else:
            #     beta = inter_time
            time = 0
            arrivals = []
            while time < self.max_simulation_time:
                time = time + round(np.random.exponential(beta))
                arrivals.append(time)
            self.arrival_times.update({row['LHRS']: arrivals})
        self.station_ranges = station_ranges
        # Create Charging Stations
        self.stations = {}
        for station_id, level_type in charging_stations.items():
            level_type = int(level_type)
            if level_type == 1:
                self.stations.update({station_id: ChargingStation(2)})
            elif level_type == 2:
                self.stations.update({station_id: ChargingStation(4)})
            elif level_type == 3:
                self.stations.update({station_id: ChargingStation(8)})
        # Initialize outputs
        self.cars_charged = {point_id: 0 for point_id in self.points}
        self.cars_not_charged = {point_id: 0 for point_id in self.points}

    # Method to find the closest station to a segment
    def get_closest_station(self, point_id, station_ranges):
        min_distance = 100000000.0
        station = None
        for station_id, distance in iter(station_ranges[point_id].items()):
            if float(distance) < min_distance:
                min_distance = float(distance)
                station = station_id
        return station, min_distance

    def simulate(self, charging_stations, station_ranges, year=2024):
        # Setup
        file = open('simulation/sim_log.txt', 'w')
        self.setup(charging_stations, station_ranges, year=year)
        station_arrivals = []  # Format = [[station_id, time, car]]
        station_departures = []  # Format = [[station_id, time]]
        # Run simulation
        for current_time in range(self.max_simulation_time):
            # Demand Generation Logic
            for point_id, arrive_list in self.arrival_times.items():
                # Generate car at this point
                while current_time == arrive_list[0]:
                    arrive_list.pop(0)  # remove arrival time
                    # self.arrival_times.update({point_id: arrive_list}) #Move to after while loop
                    car = Car(point_id)  # Create car
                    if point_id in station_ranges:  # If within range of a station
                        station_id, distance = self.get_closest_station(
                            point_id, station_ranges)
                        # Time to station in minutes
                        travel_time = round(distance / 100 * 60)
                        station_arrivals.append(
                            [station_id, current_time + travel_time, car])
                        file.write(
                            f"T{current_time}: Car appeared at {point_id}, driving for {travel_time} mins to {station_id}\n")
                    else:
                        self.cars_not_charged[point_id] += 1
                        file.write(
                            f"T{current_time}: Car appeared at {point_id}, not in range\n")
                self.arrival_times.update({point_id: arrive_list})
            # Departure Logic #include charge counts
            for index, departure in enumerate(station_departures):
                if current_time == departure[1]:
                    station_id = departure[0]
                    self.stations[station_id].car_leaves()
                    file.write(
                        f"T{current_time}: Car left station {station_id}\n")
                    if not self.stations[station_id].queue_empty():
                        charge_time, car = self.stations[station_id].start_charging(
                            current_time)
                        station_departures.append(
                            [station_id, current_time + charge_time])
                        self.cars_charged[car.get_origin()] += 1
                        file.write(
                            f"T{current_time}: Another car from {car.get_origin()} began charging at station {station_id} for {charge_time} minutes\n")
            # Station Arrival Logic
            for index, arrival in enumerate(station_arrivals):
                if current_time == arrival[1]:
                    station_id = arrival[0]
                    car = arrival[2]
                    if self.stations[station_id].add_car(car, current_time):
                        file.write(
                            f"T{current_time}: Car from {car.get_origin()} arrived at station {station_id} and entered queue\n")
                        if self.stations[station_id].chargers_free():
                            charge_time, car = self.stations[station_id].start_charging(
                                current_time)
                            station_departures.append(
                                [station_id, current_time + charge_time])
                            self.cars_charged[car.get_origin()] += 1
                            file.write(
                                f"T{current_time}: Car from {car.get_origin()} began charging at station {station_id} for {charge_time} minutes\n")
                    else:
                        file.write(
                            f"T{current_time}: Car from {car.get_origin()} arrived at station {station_id} and balked\n")
                        self.cars_not_charged[car.get_origin()] += 1

    # Method to get the coverage in each segment
    def get_coverage(self):
        if not self.cars_charged:
            raise Exception("Simulation must have been run to get coverage!")
        file = open('simulation/sim_log.txt', 'a')
        file.write(f"\n COVERAGE DICT:\n")
        coverage = {}
        for point_id, cars_charged in self.cars_charged.items():
            if cars_charged == 0 and self.cars_not_charged[point_id] == 0:
                coverage.update({point_id: -1})
            else:
                coverage.update({
                    point_id: round(
                        float(cars_charged)/(self.cars_not_charged[point_id] + cars_charged), 2)
                })
        file.write(f"{coverage}\n")
        return coverage

    # Method to get the utilization of each station
    def get_util(self):
        if not self.cars_charged:
            raise Exception("Simulation must have been run to get util!")
        file = open('simulation/sim_log.txt', 'a')
        file.write(f"\n UTIL DICT:\n")
        util = {}
        for point_id, station in self.stations.items():
            util.update(
                {point_id: round(station.get_util(self.max_simulation_time), 2)})
        file.write(f"{util}\n")
        return util

    # Method to get the avg wait time at each station
    def get_wait_times(self):
        if not self.cars_charged:
            raise Exception("Simulation must have been run to get wait times!")
        file = open('simulation/sim_log.txt', 'a')
        file.write(f"\n WAIT TIMES DICT:\n")
        wait_times = {}
        for point_id, station in self.stations.items():
            wait_times.update({point_id: station.get_avg_wait_time()})
        file.write(f"{wait_times}\n")
        return wait_times


if __name__ == '__main__':
    # Testing will break on this, just set this to points in the Simulation init
    points = [1, 2, 3, 4, 5]
    sim = Simulation()
    charging_stations = {2: 2, 5: 3}
    # Nearest charging station and distance
    station_ranges = {1: {2: 10, 5: 5}, 2: {2: 0}, 3: {2: 5}, 5: {5: 0}}
    sim.simulate(charging_stations, station_ranges)
    print(sim.get_coverage())
    print(sim.get_util())
    print(sim.get_wait_times())
