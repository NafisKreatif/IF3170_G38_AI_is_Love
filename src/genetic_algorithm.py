from data import *
import random
import math

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
        if (truck.dimensions.width >= package_dimensions.width and
            truck.dimensions.height >= package_dimensions.height and
            truck.dimensions.length >= package_dimensions.length):
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

# penalty
def kesengsaraan(config: IsekaiConfiguration):
    total = 0
    for truck in config.isekai.trucks:
        if (config.total_weight(truck) > truck.max_capacity):
            total -= config.total_weight(truck) - truck.max_capacity

    total_value = 0
    for package in config.isekai.packages:
        total_value = package.value
    avg_value = total_value // len(config.isekai.packages)

    for package in config.isekai.packages:
        if config.get_package_truck(package) is None:
            continue
        if config.package_is_outside_truck(package):
            total += avg_value // 2
        if config.package_is_intersecting(package):
            total += avg_value // 2
        if not config.package_is_supported(package):
            total += avg_value // 2
        if package.is_fragile and config.package_is_supporting(package):
            total += avg_value // 2

    return total

# main function
def dolan(isekai: Isekai, generation=1000, jumlah_penduduk=100, peluang_kelainan=0.05, persen_kaum_elit=0.05) -> IsekaiConfiguration:
    orde_lama: list[IsekaiConfiguration] = []
    for i in range(jumlah_penduduk):
        orde_lama.append(ngasal(isekai))

    # Kosong
    the_perfect_world = IsekaiConfiguration(isekai)
    the_perfect_kesejahteraan = 0

    for i in range(generation):
        print(f"Generation {i}:", the_perfect_kesejahteraan)

        total_kesejahteraan = 0
        kesejahteraan_rakyat = dict()

        # kesejahteraan awal
        first = True
        for rakyat in orde_lama:
            ks = kesejahteraan(rakyat) + kesengsaraan(rakyat)
            kesejahteraan_rakyat[rakyat] = ks
            total_kesejahteraan += ks
            # print(ks, total_kesejahteraan)
            if first:
                first = False
                termiskin_lama = ks
            else:
                termiskin_lama = min(termiskin_lama, ks)

        if termiskin_lama <= 0:
            total_kesejahteraan += (termiskin_lama + 1) * jumlah_penduduk

        orde_baru = []
        first = True
        for _ in range(jumlah_penduduk):
            rakyat1: IsekaiConfiguration
            rakyat2: IsekaiConfiguration

            random_pilih1 = random.randint(0, total_kesejahteraan - 1)
            random_pilih2 = random.randint(0, total_kesejahteraan - 1)
            for rakyat in orde_lama:
                if random_pilih1 < kesejahteraan_rakyat[rakyat] + max(0, termiskin_lama + 1):
                    rakyat1 = rakyat
                    break
                random_pilih1 -= kesejahteraan_rakyat[rakyat] + max(0, termiskin_lama + 1)
            for rakyat in orde_lama:
                if random_pilih2 < kesejahteraan_rakyat[rakyat] + max(0, termiskin_lama + 1):
                    rakyat2 = rakyat
                    break
                random_pilih2 -= kesejahteraan_rakyat[rakyat] + max(0, termiskin_lama + 1)

            bocah = kawin(rakyat1, rakyat2)
            orde_baru.append(bocah[0])
            orde_baru.append(bocah[1])
            kesejahteraan_rakyat[bocah[0]] = kesejahteraan(bocah[0]) + kesengsaraan(bocah[0])
            kesejahteraan_rakyat[bocah[1]] = kesejahteraan(bocah[1]) + kesengsaraan(bocah[1])
           
        for bocah in orde_baru:
            total_kesejahteraan += kesejahteraan_rakyat[bocah]
            if first:
                first = False
                termiskin_baru = kesejahteraan_rakyat[bocah]
            else:
                termiskin_baru = min(termiskin_baru, kesejahteraan_rakyat[bocah])

        if termiskin_lama < termiskin_baru:
            total_kesejahteraan += (termiskin_lama + 1) * (2 * jumlah_penduduk)
        elif termiskin_baru <= 0:
            total_kesejahteraan += (termiskin_baru + 1) * (3 * jumlah_penduduk) - (termiskin_lama + 1) * jumlah_penduduk
        termiskin = min(termiskin_lama, termiskin_baru)

        orde_lama.sort(key = lambda rakyat: kesejahteraan_rakyat[rakyat], reverse=True)
        for i in range(math.ceil(persen_kaum_elit * len(orde_lama)), len(orde_lama)):
            if random.random() < peluang_kelainan:
                kelainan(orde_lama[i])

        for i in range(len(orde_baru)):
            if random.random() < peluang_kelainan:
                kelainan(orde_baru[i])

        orde_terbaru = []
        for i in range(0, math.ceil(persen_kaum_elit * len(orde_lama))):
            orde_terbaru.append(orde_lama[i])

        while len(orde_terbaru) < jumlah_penduduk:
            sudah_dipilih = False
            random_pilih = random.randint(0, total_kesejahteraan - 1)
            for rakyat in orde_lama:
                if random_pilih < kesejahteraan_rakyat[rakyat] + max(0, termiskin + 1):
                    orde_terbaru.append(rakyat)
                    sudah_dipilih = True
                    break
                random_pilih -= kesejahteraan_rakyat[rakyat] + max(0, termiskin + 1)
            if sudah_dipilih: continue
            for rakyat in orde_baru:
                if random_pilih < kesejahteraan_rakyat[rakyat] + max(0, termiskin + 1):
                    orde_terbaru.append(rakyat)
                    break
                random_pilih -= kesejahteraan_rakyat[rakyat] + max(0, termiskin + 1)

        for rakyat in orde_terbaru:
            if rakyat.is_valid() and kesejahteraan_rakyat[rakyat] > the_perfect_kesejahteraan:
                the_perfect_world = rakyat
                the_perfect_kesejahteraan = kesejahteraan_rakyat[rakyat]
        orde_lama = orde_terbaru

    print(f"Generation {generation}:", the_perfect_kesejahteraan)
    return the_perfect_world



isekai = load_isekai_from_file("data/testcase_8.json")
total_value = 0
for package in isekai.packages:
    total_value += package.value

print("Max possible value:", total_value)
result = dolan(isekai, generation=1000, jumlah_penduduk=100, peluang_kelainan=0.05)

# print(kesejahteraan(result))