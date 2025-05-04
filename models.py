import math
from copy import deepcopy

class Package:
    def __init__(self, id, x, y, weight, priority):
        self.id = id
        self.x = x
        self.y = y
        self.weight = weight
        self.priority = priority

    def destination(self):
        return (self.x, self.y)

    def __repr__(self):
        return f"Package(id={self.id}, weight={self.weight:.1f}, priority={self.priority}, dest=({self.x:.1f},{self.y:.1f}))"

class Vehicle:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity
        self.packages = []

    def current_load(self):
        return sum(pkg.weight for pkg in self.packages)

    def can_add(self, pkg):
        return self.current_load() + pkg.weight <= self.capacity

    def route(self):
        return [(0, 0)] + [pkg.destination() for pkg in self.packages] + [(0, 0)]

    def distance(self):
        coords = self.route()
        return sum(euclidean(coords[i], coords[i + 1]) for i in range(len(coords) - 1))

    def __repr__(self):
        return f"Vehicle {self.id} | Load: {self.current_load():.1f}/{self.capacity} | Packages: {[p.id for p in self.packages]}"

class DeliverySolution:
    def __init__(self, vehicles):
        self.vehicles = vehicles

    def total_distance(self):
        return sum(vehicle.distance() for vehicle in self.vehicles)

    def is_valid(self):
        return all(vehicle.current_load() <= vehicle.capacity for vehicle in self.vehicles)

    def clone(self):
        return deepcopy(self)

    def __repr__(self):
        return f"\nTotal Distance: {self.total_distance():.2f} km\n" + "\n".join(str(v) for v in sorted(self.vehicles, key=lambda v: v.id))

def euclidean(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
