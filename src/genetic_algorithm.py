from data import *
import random

def ngasal(isekai: Isekai) -> IsekaiConfiguration:
    config = IsekaiConfiguration(isekai)

    for package in isekai.packages:
        kelempar(config, package)

    return config 

# crossover
def kawin(config1: IsekaiConfiguration, config2: IsekaiConfiguration):
    isekai = config1.isekai;
    other_world_1 = IsekaiConfiguration(isekai)
    other_world_2 = IsekaiConfiguration(isekai)

    for truck in isekai.trucks:
        point_of_no_return = random.randint(0, truck.dimensions.height)
                
        for package in isekai.packages:
            if config1.get_package_truck(package) is truck:
                position = config1.get_package_position(package)
                orientation = config1.get_package_orientation(package)
                if position.y < point_of_no_return:
                    if other_world_1.get_package_truck(package) is None:
                        other_world_1.configure_package(package, truck, position, orientation)
                else:
                    if other_world_2.get_package_truck(package) is None:
                        other_world_2.configure_package(package, truck, position, orientation)
            if config2.get_package_truck(package) is truck:
                position = config2.get_package_position(package)
                orientation = config2.get_package_orientation(package)
                if position.y < point_of_no_return:
                    if other_world_2.get_package_truck(package) is None:
                        other_world_2.configure_package(package, truck, position, orientation)
                else:
                    if other_world_1.get_package_truck(package) is None:
                        other_world_1.configure_package(package, truck, position, orientation)

    return [other_world_1, other_world_2]

# position mutation
def kesenggol(config: IsekaiConfiguration, package: LovePackage = None):
    if package is None:
        package = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]
    position = config.get_package_position(package)

    if position is None:
        return

    truck = config.get_package_truck(package)

    position.x = random.randint(0, truck.dimensions.width)
    position.y = random.randint(0, truck.dimensions.height)
    position.z = random.randint(0, truck.dimensions.length)

# orientation mutation
def keguling(config: IsekaiConfiguration, package: LovePackage = None):
    if package is None:
        package = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]
    orientation = config.get_package_orientation(package)

    if orientation is None:
        return

    match random.randint(0, 2):
        case 0:
            temp = orientation.width_orientation
            orientation.width_orientation = orientation.height_orientation
            orientation.height_orientation = temp
        case 1:
            temp = orientation.width_orientation
            orientation.width_orientation = orientation.length_orientation
            orientation.length_orientation = temp
        case 2:
            temp = orientation.length_orientation
            orientation.length_orientation = orientation.height_orientation
            orientation.height_orientation = temp

# menukar dua paket
def ketukar(config: IsekaiConfiguration):
    package1 = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]
    package2 = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]
    truck1 = config.get_package_truck(package1)
    truck2 = config.get_package_truck(package2)
    position1 = config.get_package_position(package1)
    position2 = config.get_package_position(package2)
    orientation1 = config.get_package_orientation(package1)
    orientation2 = config.get_package_orientation(package2)
    config.configure_package(package1, truck2, position2, orientation2)
    config.configure_package(package2, truck1, position1, orientation1)

# masuk keluar paket dari truck
def kelempar(config: IsekaiConfiguration, package: LovePackage = None):
    if package is None:
        package = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]
    truck = config.get_package_truck(package)

    if truck is None:
        truck = config.isekai.trucks[random.randint(0, len(config.isekai.trucks) - 1)]
        package_dimensions = Dimensions(0, 0, 0)
        match package.orientation.width_orientation:
            case "x": package_dimensions.width += package.dimensions.width
            case "y": package_dimensions.height += package.dimensions.width
            case "z": package_dimensions.length += package.dimensions.width
        match package.orientation.height_orientation:
            case "x": package_dimensions.width += package.dimensions.height
            case "y": package_dimensions.height += package.dimensions.height
            case "z": package_dimensions.length += package.dimensions.height
        match package.orientation.length_orientation:
            case "x": package_dimensions.width += package.dimensions.length
            case "y": package_dimensions.height += package.dimensions.length
            case "z": package_dimensions.length += package.dimensions.length
        random_position = Position(random.randint(0, truck.dimensions.width - package_dimensions.width),
                                   random.randint(0, truck.dimensions.height - package_dimensions.height),
                                   random.randint(0, truck.dimensions.length - package_dimensions.length))
        config.configure_package(package, truck, random_position, package.orientation)
    else:
        config.remove_package(package)

# mutasi
def kelainan(config: IsekaiConfiguration):
    match random.randint(0, 3):
        case 0: kesenggol(config)
        case 1: keguling(config)
        case 2: ketukar(config)
        case 3: kelempar(config)

# objective function
def kesejahteraan(config: IsekaiConfiguration):
    total = 0
    for truck in config.isekai.trucks:
        if config.is_truck_valid(truck):
            for package in config.isekai.packages:
                if config.get_package_truck(package) is truck:
                    total += package.value
    return total

# main function
def dolan(isekai: Isekai, generation=1000, penduduk=100, mutate_peluang=0.05) -> IsekaiConfiguration:
    list_wonge: list[IsekaiConfiguration] = []
    for i in range(penduduk):
        list_wonge.append(ngasal(isekai))

    # Kosong
    the_perfect_world = IsekaiConfiguration(isekai)

    for i in range(generation):
        print(f"Generation {i}: ", kesejahteraan(the_perfect_world))

        total_kesejahteraan = 0
        list_kesejahteraan = []
        for wonge in list_wonge:
            ks = kesejahteraan(wonge)
            list_kesejahteraan.append(ks)
            total_kesejahteraan += ks

        persen_kesejahteraan = []
        for ks in list_kesejahteraan:
            if total_kesejahteraan > 0:
                persen_kesejahteraan.append(ks / total_kesejahteraan)
            else:
                persen_kesejahteraan.append(1 / len(list_kesejahteraan))

        for k in range(penduduk):
            random_pilih1 = random.random()
            random_pilih2 = random.random()

            wong1: IsekaiConfiguration
            wong2: IsekaiConfiguration
            for j in range(penduduk):
                if random_pilih1 < persen_kesejahteraan[j]:
                    wong1 = list_wonge[j]
                    break
                random_pilih1 -= persen_kesejahteraan[j]
            for j in range(penduduk):
                if random_pilih2 < persen_kesejahteraan[j]:
                    wong2 = list_wonge[j]
                    break
                random_pilih2 -= persen_kesejahteraan[j]

            bocah = kawin(wong1, wong2)
            list_wonge.append(bocah[0])
            list_wonge.append(bocah[1])
            ks1 = kesejahteraan(bocah[0])
            ks2 = kesejahteraan(bocah[1])
            list_kesejahteraan.append(ks1)
            list_kesejahteraan.append(ks2)
            total_kesejahteraan += ks1 + ks2

        for wonge in list_wonge:
            if random.random() < mutate_peluang:
                kelainan(wonge)

        persen_kesejahteraan = []
        for ks in list_kesejahteraan:
            if total_kesejahteraan > 0:
                persen_kesejahteraan.append(ks / total_kesejahteraan)
            else:
                persen_kesejahteraan.append(1 / len(list_kesejahteraan))

        wong_baru = []
        for i in range(penduduk):
            random_pilih = random.random()
            for j in range(len(list_wonge)):
                if random_pilih < persen_kesejahteraan[j]:
                    wong_baru.append(list_wonge[j])
                    break
                random_pilih -= persen_kesejahteraan[j]

        list_wonge = wong_baru
        for wong in list_wonge:
            if wong.is_valid() and kesejahteraan(wong) > kesejahteraan(the_perfect_world):
                the_perfect_world = wong.copy()

    print(f"Generation {generation}: ", kesejahteraan(the_perfect_world))
    return the_perfect_world



# isekai = load_isekai_from_file("data/testcase_1.json")
# result = dolan(isekai, generation=1000, penduduk=100, mutate_peluang=0.05)

# print(kesejahteraan(result))