import json

class Dimensions:
    def __init__(self, width, length, height):
        self.width = width
        self.length = length
        self.height = height

class Orientation:
    def __init__(self, width_orientation = "x", length_orientation = "z", height_orientation = "y"):
        self.width_orientation = width_orientation
        self.length_orientation = length_orientation
        self.height_orientation = height_orientation

class TruckKun:
    id_count = 0
    def __init__(self, id = "truck_" + id_count, dimensions = Dimensions(10, 10, 10), max_capacity = 1000):
        self.id = id
        self.dimensions = dimensions
        self.max_capacity = max_capacity

        if id == "truck_" + self.id_count:
            id_count += 1
            
class LovePackage:
    id_count = 0

    def __init__(self, id = "package_" + id_count,
                 dimensions = Dimensions(10, 10, 10),
                 orientation = Orientation("x", "y", "z"),
                 value = 10,
                 weight = 10,
                 is_fragile = False,
                 estimated_time_of_arrival = 1):
        self.id = id
        self.dimensions = dimensions
        self.orientation = orientation
        self.value = value
        self.weight = weight
        self.is_fragile = is_fragile,
        self.estimated_time_of_arrival = estimated_time_of_arrival

        if id == "package_" + self.id_count:
            id_count += 1

class Isekai:
    def __init__(self, trucks: list[TruckKun], packages: list[LovePackage]):
        self.trucks = trucks
        self.packages = packages

def truck_from_obj(obj):
    if obj["type"] != "truck":
        return None
    else:
        return TruckKun(obj["id"],
                        Dimensions(obj["dimensions"]["w"], obj["dimensions"]["l"], obj["dimensions"]["h"]),
                        obj["max_capacity"])

def truck_to_obj(truck: TruckKun):
    return {
        "id" : truck.id,
        "dimensions" : {"w": truck.dimensions.width, "l": truck.dimensions.length, "h": truck.dimensions.height},
        "max_capacity" : truck.max_capacity
    }

def package_from_obj(obj):
    if obj["type"] != "package":                                                                     
        return None
    else:
        return LovePackage(obj["id"],
                        Dimensions(obj["dimensions"]["w"], obj["dimensions"]["l"], obj["dimensions"]["h"]),
                        Orientation(obj["orientation"]["w"], obj["orientation"]["l"], obj["orientation"]["h"]),
                        obj["value"],
                        obj["weight"],
                        obj["is_fragile"],
                        obj["estimated_time_of_arrival"])

def package_to_obj(package: LovePackage):
    return {
        "id" : package.id,
        "dimensions" : {
            "w": package.dimensions.width,
            "l": package.dimensions.length,
            "h": package.dimensions.height
        },
        "orientation" : {
            "w": package.orientation.width_orientation,
            "l": package.orientation.length_orientation,
            "h": package.orientation.height_orientation
        },
        "value": package.value,
        "weight": package.weight,
        "is_fragile": package.is_fragile,
        "estimated_time_of_arrival": package.estimated_time_of_arrival
    }

def parse_isekai(json_string: str):
    truckKuns = []
    lovePackages = []

    objs = json.load(json_string)
    for obj in objs:
        if obj["type"] == "package":
            lovePackages.append(package_from_obj(obj))
        elif obj["type"] == "truck":
            truckKuns.append(truck_from_obj(obj))

    return Isekai(truckKuns, lovePackages)

def load_isekai_from_file(filepath: str):
    with open(filepath, "r") as file:
        result = parse_isekai(file.read())
    return result

def isekai_to_str(isekai: Isekai):
    objs = []
    for truck in isekai.trucks:
        objs.append(truck)
    for package in isekai.packages:
        objs.append(package)
    return json.dumps(objs)
    
def save_isekai_to_file(isekai: Isekai, filepath: str):
    with open(filepath, "w") as file:
        file.write(isekai_to_str(isekai))