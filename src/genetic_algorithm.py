from data import *
import random
import math
import time

# random inital state
def ngasal(isekai: Isekai) -> IsekaiConfiguration:
    config = IsekaiConfiguration(isekai)

    for package in isekai.packages:
        kelempar(config, package)

    order = dict[TruckKun, list]()

    for truck in isekai.trucks:
        order[truck] = []
        for package in isekai.packages:
            if config.get_package_truck(package) is truck:
                order[truck].append(package)
        random.shuffle(order[truck])    
        for package in order[truck]:
            position = config.get_package_position(package)
            position.y = 0
            for other_package in order[truck]:
                if package == other_package: break
                bound = config.calculate_bound(package)
                other_bound = config.calculate_bound(other_package)
                if not (bound[1].x <= other_bound[0].x
                        or bound[0].x >= other_bound[1].x
                        or bound[1].z <= other_bound[0].z
                        or bound[0].z >= other_bound[1].z):
                    position.y = max(position.y, other_bound[1].y)
            config.set_package_position(package, position)

    for package in isekai.packages:
        if config.package_is_outside_truck(package) or package.is_fragile and config.package_is_supporting(package):
            config.remove_package(package)

    for truck in isekai.trucks:
        for package in order[truck]:
            if config.get_package_truck(package) is not truck:
                continue
            position = config.get_package_position(package)
            position.y = 0
            for other_package in order[truck]:
                if package == other_package: break
                if config.get_package_truck(other_package) is not truck:
                    continue
                bound = config.calculate_bound(package)
                other_bound = config.calculate_bound(other_package)
                if not (bound[1].x <= other_bound[0].x
                        or bound[0].x >= other_bound[1].x
                        or bound[1].z <= other_bound[0].z
                        or bound[0].z >= other_bound[1].z):
                    position.y = max(position.y, other_bound[1].y)
            config.set_package_position(package, position)

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

    truck = config.get_package_truck(package)
    if truck is None:
        return

    package_dimensions = config.get_package_dimensions(package)

    if (truck.dimensions.width >= package_dimensions.width and
        truck.dimensions.height >= package_dimensions.height and
        truck.dimensions.length >= package_dimensions.length):
        random_position = Position(random.randint(0, truck.dimensions.width - package_dimensions.width),
                                random.randint(0, truck.dimensions.height - package_dimensions.height),
                                random.randint(0, truck.dimensions.length - package_dimensions.length))
        config.set_package_position(package, random_position)

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
    config.set_package_orientation(package, orientation)   

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
        orientation_value = ["x", "y", "z"]
        random.shuffle(orientation_value)
        orientation = Orientation(orientation_value[0], orientation_value[1], orientation_value[2])
        config.set_package_orientation(package, orientation)
        package_dimensions = config.get_package_dimensions(package)
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
def kesejahteraan(config: IsekaiConfiguration, check_validity: bool = False):
    total = 0
    for truck in config.isekai.trucks:
        if not check_validity or config.is_truck_valid(truck):
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
        total_value += package.value
    avg_value = total_value // len(config.isekai.packages)

    for package in config.isekai.packages:
        if config.get_package_truck(package) is None:
            continue
        if config.package_is_outside_truck(package):
            total -= avg_value // 2
        if config.package_is_intersecting(package):
            total -= avg_value // 2
        if not config.package_is_supported(package):
            total -= avg_value // 2
        if package.is_fragile and config.package_is_supporting(package):
            total -= avg_value // 2

    return total

# main function
def dolan(isekai: Isekai, generation=1000, jumlah_penduduk=100, peluang_kelainan=0.05, persen_kaum_elit=0.05, debug=False, seed:int=None) -> dict:
    random.seed(seed)

    start_time = time.perf_counter()
    
    orde_lama: list[IsekaiConfiguration] = []
    for i in range(jumlah_penduduk):
        orde_lama.append(ngasal(isekai))

    the_first_world: IsekaiConfiguration # best initial state
    the_first_kesejahteraan = 0 # best initial value
    the_perfect_world: IsekaiConfiguration # best final state
    the_perfect_kesejahteraan = 0
    list_termiskin = []
    list_termakmur = []
    list_terbiasa = []
    list_perfect = []

    the_perfect_world = IsekaiConfiguration(isekai)
    the_perfect_kesejahteraan = 0
    kesejahteraan_rakyat = dict[IsekaiConfiguration, int]()

    for i in range(generation):
        # Perhitungan statistik
        termiskin = 0
        termakmur = 0
        terbiasa = 0
        total_kesejahteraan = 0
    
        first = True
        for rakyat in orde_lama:
            if rakyat not in kesejahteraan_rakyat:
                ks = kesejahteraan(rakyat) + kesengsaraan(rakyat)
                kesejahteraan_rakyat[rakyat] = ks
            else:
                ks = kesejahteraan_rakyat[rakyat]
            total_kesejahteraan += ks
            if rakyat.is_valid() and ks > the_perfect_kesejahteraan:
                the_perfect_world = rakyat.copy()
                the_perfect_kesejahteraan = ks
            if first:
                first = False
                termiskin = ks
                termakmur = ks
            else:
                termiskin = min(termiskin, ks)
                termakmur = max(termakmur, ks)
        terbiasa = total_kesejahteraan / jumlah_penduduk

        # Buat initial state
        if i == 0:
            the_first_world = the_perfect_world
            the_first_kesejahteraan = the_perfect_kesejahteraan
    
        list_termiskin.append(termiskin)
        list_termakmur.append(termakmur)
        list_terbiasa.append(terbiasa) 
        list_perfect.append(the_perfect_kesejahteraan)

        if debug:
            print(f"Generation {i}:")
            print(f" -> termakmur =", termakmur)
            print(f" -> terbiasa =", terbiasa)
            print(f" -> termiskin =", termiskin)
            print(f" -> varietas =", len(kesejahteraan_rakyat))

        # Anggapannya seperti menggeser semua kesejahteraan biar tidak ada yang negatif dan nol
        if termiskin <= 0:
            total_kesejahteraan += (-termiskin + 1) * jumlah_penduduk

        # Generate offspring
        orde_baru = list[IsekaiConfiguration]()
        for _ in range(jumlah_penduduk):
            rakyat1: IsekaiConfiguration
            rakyat2: IsekaiConfiguration

            random_pilih1 = random.randint(0, total_kesejahteraan - 1)
            random_pilih2 = random.randint(0, total_kesejahteraan - 1)
            for rakyat in orde_lama:
                if random_pilih1 < kesejahteraan_rakyat[rakyat] + max(0, -termiskin + 1):
                    rakyat1 = rakyat
                    break
                random_pilih1 -= kesejahteraan_rakyat[rakyat] + max(0, -termiskin + 1)
            for rakyat in orde_lama:
                if random_pilih2 < kesejahteraan_rakyat[rakyat] + max(0, -termiskin + 1):
                    rakyat2 = rakyat
                    break
                random_pilih2 -= kesejahteraan_rakyat[rakyat] + max(0, -termiskin + 1)

            bocah = kawin(rakyat1, rakyat2)
            orde_baru.append(bocah[0])
            orde_baru.append(bocah[1])

        # Mutasi populasi lama dan offspring, kecuali kaum elit dari populasi lama
        # Sekalian hitung ulang kesejahteraan populasi lama jika perlu
        # Hitung juga kesejahteraan offspring karena belum
        orde_lama.sort(key = lambda rakyat: kesejahteraan_rakyat[rakyat], reverse=True)
        for i in range(math.ceil(persen_kaum_elit * len(orde_lama)), len(orde_lama)):
            if random.random() < peluang_kelainan:
                kelainan(orde_lama[i])
                kesejahteraan_rakyat[orde_lama[i]] = kesejahteraan(orde_lama[i]) + kesengsaraan(orde_lama[i])
        for i in range(len(orde_baru)):
            if random.random() < peluang_kelainan:
                kelainan(orde_baru[i])
            kesejahteraan_rakyat[orde_baru[i]] = kesejahteraan(orde_baru[i]) + kesengsaraan(orde_baru[i])

        # Hitung ulang kesejahteraan, buat seleksi nanti
        total_kesejahteraan = 0
        first = True
        for rakyat in orde_lama:
            total_kesejahteraan += kesejahteraan_rakyat[rakyat]
            if first:
                first = False
                termiskin = kesejahteraan_rakyat[rakyat]
            else:
                termiskin = min(termiskin, kesejahteraan_rakyat[rakyat])
        for rakyat in orde_baru:
            total_kesejahteraan += kesejahteraan_rakyat[rakyat]
            if first:
                first = False
                termiskin = kesejahteraan_rakyat[rakyat]
            else:
                termiskin = min(termiskin, kesejahteraan_rakyat[rakyat])

        # Anggapannya seperti menggeser semua kesejahteraan biar tidak ada yang negatif dan nol
        if termiskin <= 0:
            total_kesejahteraan += (-termiskin + 1) * 3 * jumlah_penduduk

        # Seleksi dari populasi lama dan baru, kaum elit ngebayar biar langsung lolos seleksi
        orde_terbaru = []
        for i in range(0, math.ceil(persen_kaum_elit * len(orde_lama))):
            orde_terbaru.append(orde_lama[i])
        while len(orde_terbaru) < jumlah_penduduk:
            sudah_pilih = False
            random_pilih = random.randint(0, total_kesejahteraan - 1)
            for rakyat in orde_lama:
                if random_pilih < kesejahteraan_rakyat[rakyat] + max(0, termiskin + 1):
                    orde_terbaru.append(rakyat)
                    sudah_pilih = True
                    break
                random_pilih -= kesejahteraan_rakyat[rakyat] + max(0, termiskin + 1)
            if sudah_pilih: continue
            for rakyat in orde_baru:
                if random_pilih < kesejahteraan_rakyat[rakyat] + max(0, termiskin + 1):
                    orde_terbaru.append(rakyat)
                    break
                random_pilih -= kesejahteraan_rakyat[rakyat] + max(0, termiskin + 1)

        # Hasil yang betulan valid, ga cuma dari fitness
        for rakyat, ks in kesejahteraan_rakyat.items():
            if rakyat.is_valid() and ks > the_perfect_kesejahteraan:
                the_perfect_world = rakyat.copy()
                the_perfect_kesejahteraan = ks

        # Hapus konfigurasi yang ga masuk jadi generasi berikutnya
        rakyat_mati = []
        for rakyat in kesejahteraan_rakyat.keys():
            if rakyat not in orde_terbaru:
                rakyat_mati.append(rakyat)

        for rakyat in rakyat_mati:
            kesejahteraan_rakyat.pop(rakyat)
    
        orde_lama = orde_terbaru

    # Hitung statistik akhir
    termiskin = 0
    termakmur = 0
    terbiasa = 0
    total_kesejahteraan = 0

    first = True
    for rakyat in orde_lama:
        if rakyat not in kesejahteraan_rakyat:
            ks = kesejahteraan(rakyat) + kesengsaraan(rakyat)
            kesejahteraan_rakyat[rakyat] = ks
        else:
            ks = kesejahteraan_rakyat[rakyat]
        total_kesejahteraan += ks
        if rakyat.is_valid() and ks > the_perfect_kesejahteraan:
            the_perfect_world = rakyat.copy()
            the_perfect_kesejahteraan = ks
        if first:
            first = False
            termiskin = ks
            termakmur = ks
        else:
            termiskin = min(termiskin, ks)
            termakmur = max(termakmur, ks)
    terbiasa = total_kesejahteraan / jumlah_penduduk

    list_termiskin.append(termiskin)
    list_termakmur.append(termakmur)
    list_terbiasa.append(terbiasa)
    list_perfect.append(the_perfect_kesejahteraan)

    if debug:
        print(f"Generation {generation}:")
        print(f" -> termakmur =", termakmur)
        print(f" -> terbiasa =", terbiasa)
        print(f" -> termiskin =", termiskin)
        print(f" -> varietas =", len(kesejahteraan_rakyat))
    
    return  {
        "initial_state": the_first_world,
        "final_state": the_perfect_world,
        "initial_value": the_first_kesejahteraan,
        "final_value": the_perfect_kesejahteraan,
        "best_value_history": list_perfect,
        "max_fitness_history": list_termakmur,
        "avg_fitness_history": list_terbiasa,
        "min_fitness_history": list_termiskin,
        "iterations": generation,
        "populations": jumlah_penduduk,
        "duration": time.perf_counter() - start_time
    }

if __name__ == "__main__":
    isekai = load_isekai_from_file("data/2_trucks_50_packages.json")
    total_value = 0
    for package in isekai.packages:
        total_value += package.value

    result = dolan(isekai, generation=1000, jumlah_penduduk=100, peluang_kelainan=0.05, persen_kaum_elit=0.02, debug=True)
    print("Max possible value:", total_value)
    print("Value akhir:", kesejahteraan(result["final_state"]))
    print("Persen keberhasilan:", f"{round(kesejahteraan(result["final_state"]) / total_value * 100, 2)}%")