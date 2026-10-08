import json

class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Dimensions:
    def __init__(self, width, length, height):
        self.width = width
        self.length = length
        self.height = height

class Orientation:
    def __init__(self, width_orientation = "x", length_orientation = "y", height_orientation = "z"):
        self.width_orientation = width_orientation
        self.length_orientation = length_orientation
        self.height_orientation = height_orientation

class TruckKun:
    id_count = 0
    def __init__(self, id = "truck_" + str(id_count), dimensions = Dimensions(10, 10, 10), max_capacity = 1000):
        self.id = id
        self.dimensions = dimensions
        self.max_capacity = max_capacity

        if id == "truck_" + str(self.id_count):
            TruckKun.id_count += 1
            
            
class LovePackage:
    id_count = 0

    def __init__(self, id = "package_" + str(id_count),
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
        self.is_fragile = is_fragile
        self.estimated_time_of_arrival = estimated_time_of_arrival

        if id == "package_" + str(self.id_count):
            LovePackage.id_count += 1

class Isekai:
    def __init__(self, trucks: list[TruckKun], packages: list[LovePackage]):
        self.trucks = trucks
        self.packages = packages
        
class IsekaiConfiguration():
    def __init__(self, isekai: Isekai):
        self.isekai = isekai

        self.package_truck = dict[LovePackage, TruckKun]() # package -> truck
        self.package_position = dict[LovePackage, Position]() # package -> position
        self.package_orientation = dict[LovePackage, Orientation]() # package -> orientation
         
    def configure_package(self, package: LovePackage, truck: TruckKun, position: Position = Position(0, 0, 0), orientation: Orientation = Orientation()) -> bool:
        self.package_truck[package] = truck
        self.package_position[package] = position
        self.package_orientation[package] = orientation
        return self.is_valid()

    def remove_package(self, package: LovePackage) -> bool:
        self.package_truck.pop(package)
        self.package_position.pop(package)
        self.package_orientation.pop(package)
        return self.is_valid()

    def set_package_truck(self, package: LovePackage, truck: TruckKun) -> bool:
        self.package_truck[package] = truck
        return self.is_valid()

    def set_package_position(self, package: LovePackage, position: Position) -> bool:
        self.package_position[package] = position
        return self.is_valid()

    def set_package_orientation(self, package: LovePackage, orientation: Orientation) -> bool:
        self.package_orientation[package] = orientation
        return self.is_valid()

    def get_package_truck(self, package: LovePackage) -> TruckKun:    
        return self.package_truck.get(package)

    def get_package_position(self, package: LovePackage) -> Position:    
            return self.package_position.get(package)

    def get_package_orientation(self, package: LovePackage) -> Orientation:    
            return self.package_orientation.get(package)
    def package_is_outside_truck(self, package:LovePackage) -> bool:
        truck = self.get_package_truck(package)

        if truck is None:
            return False

        bounds = self.calculate_bound(package)

        return (
            bounds[0].x < 0
            or bounds[0].y < 0
            or bounds[0].z < 0
            or bounds[1].x > truck.dimensions.width
            or bounds[1].y > truck.dimensions.length
            or bounds[1].z > truck.dimensions.height
        )
    
    def is_valid(self) -> bool:
        valid = True

        for truck in self.isekai.trucks:
            if (self.total_weight(truck) > truck.max_capacity):
                valid = False
            if not valid: break

        for package in self.isekai.packages:
            if self.get_package_truck(package) is None:
                continue
            if self.package_is_outside_truck(package):
                valid = False
            if self.package_is_intersecting(package):
                valid = False
            if not self.package_is_supported(package):
                valid = False
            if package.is_fragile and self.package_is_supporting(package):
                valid = False
            if not valid: break

        return valid

    def total_weight(self, truck: TruckKun):
        total = 0
        for package, truckKun in self.package_truck.items():
            if truck is truckKun:
                total += package.weight
        return total

    def package_is_supported(self, package: LovePackage) -> bool:
        if self.get_package_truck(package) is None:
            return True
        
        bounds = self.calculate_bound(package)
        if bounds[0].z == 0:
            return True

        for other_package in self.isekai.packages:
            if package is other_package:
                            continue
            if self.get_package_truck(package) is not self.get_package_truck(other_package):
                continue
            other_bounds = self.calculate_bound(other_package)
            intersecting_area = not (
                bounds[1].x <= other_bounds[0].x
                or bounds[0].x >= other_bounds[1].x
                or bounds[1].y <= other_bounds[0].y
                or bounds[0].y >= other_bounds[1].y
            )
            if intersecting_area and bounds[0].z == other_bounds[1].z:
                return True
        
        return False
    
    def package_is_supporting(self, package: LovePackage) -> bool:
        if self.get_package_truck(package) is None:
            return False
        
        bounds = self.calculate_bound(package)
        for other_package in self.isekai.packages:
            if package is other_package:
                            continue
            if self.get_package_truck(package) is not self.get_package_truck(other_package):
                continue
            other_bounds = self.calculate_bound(other_package)
            intersecting_area = not (
                bounds[1].x <= other_bounds[0].x
                or bounds[0].x >= other_bounds[1].x
                or bounds[1].y <= other_bounds[0].y
                or bounds[0].y >= other_bounds[1].y
            )
            if intersecting_area and bounds[1].z == other_bounds[0].z:
                return True
        
        return False
    
    def calculate_bound(self, package: LovePackage) -> list[Position]:
        first_point = self.get_package_position(package)
        other_point = Position(first_point.x, first_point.y, first_point.z)
        orientation = self.get_package_orientation(package)
        match orientation.width_orientation:
            case "x": other_point.x += package.dimensions.width
            case "y": other_point.y += package.dimensions.width
            case "z": other_point.z += package.dimensions.width
        match orientation.height_orientation:
            case "x": other_point.x += package.dimensions.height
            case "y": other_point.y += package.dimensions.height
            case "z": other_point.z += package.dimensions.height
        match orientation.length_orientation:
            case "x": other_point.x += package.dimensions.length
            case "y": other_point.y += package.dimensions.length
            case "z": other_point.z += package.dimensions.length
        return [first_point, other_point]
        
    def package_is_intersecting(self, package: LovePackage) -> bool:
        if self.get_package_truck(package) is None:
            return False
        
        intersecting = False
        bounds = self.calculate_bound(package)
        for other_package in self.isekai.packages:
            if package is other_package:
                continue
            if self.get_package_truck(package) is not self.get_package_truck(other_package):
                continue
            other_bounds = self.calculate_bound(other_package)
            if not (
                bounds[1].x <= other_bounds[0].x
                or bounds[0].x >= other_bounds[1].x
                or bounds[1].y <= other_bounds[0].y
                or bounds[0].y >= other_bounds[1].y
                or bounds[1].z <= other_bounds[0].z
                or bounds[0].z >= other_bounds[1].z
            ):
                intersecting = True
                break

        return intersecting

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

    objs = json.loads(json_string)
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