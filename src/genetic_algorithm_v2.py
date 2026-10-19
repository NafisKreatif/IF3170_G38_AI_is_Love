from data import *
import random
import math
import time


class IsekaiOrder(IsekaiConfiguration):
    def __init__(self, isekai: Isekai):
        super().__init__(isekai)
        self.package_order = dict[TruckKun, list[LovePackage]]()
        for truck in isekai.trucks:
            self.package_order[truck] = list[LovePackage]()


    def configure_package(self, package: LovePackage, truck: TruckKun, position: Position = Position(0, 0, 0), orientation: Orientation = Orientation(), order: int = -1):
        super().configure_package(package, truck, position, orientation)
        self.set_package_order(package, order)


    def remove_package(self, package: LovePackage):
        truck = self.get_package_truck(package)
        if truck is not None and self.package_order[truck].count(package) > 0:
            self.package_order[truck].remove(package)
        super().remove_package(package)
    

    def set_package_truck(self, package: LovePackage, truck: TruckKun, order: int = -1):
        prev_truck = self.get_package_truck(package)
        if prev_truck is not None:
            self.package_order[prev_truck].remove(package)

        self.package_truck[package] = truck

        if truck is not None:
            if order == -1:
                order = random.randint(0, len(self.package_order[truck]))
            self.package_order[truck].insert(order, package)


    def set_package_order(self, package: LovePackage, order: int) -> bool:
        truck = self.get_package_truck(package)
        if truck is not None:
            if self.package_order[truck].count(package) > 0:
                self.package_order[truck].remove(package)
            if order == -1:
                order = random.randint(0, len(self.package_order[truck]))
            self.package_order[truck].insert(order, package)


    def get_package_order(self, package: LovePackage) -> bool:
        truck = self.get_package_truck(package)
        if truck is not None and self.package_order[truck].count(package) > 0:
            return self.package_order[truck].index(package)
        else:
            return -1


    def recalculate_position(self):
        for packages in self.package_order.values():
            for package in packages:
                position = self.get_package_position(package)
                position.y = 0
                for other_package in packages:
                    if package == other_package: break
                    bound = self.calculate_bound(package)
                    other_bound = self.calculate_bound(other_package)
                    if not (bound[1].x <= other_bound[0].x
                            or bound[0].x >= other_bound[1].x
                            or bound[1].z <= other_bound[0].z
                            or bound[0].z >= other_bound[1].z):
                        position.y = max(position.y, other_bound[1].y)


    def copy(self) -> IsekaiOrder:
        config = IsekaiOrder(self.isekai)
        config.package_truck = self.package_truck.copy()
        config.package_position = self.package_position.copy()
        config.package_orientation = self.package_orientation.copy()
        for truck in self.isekai.trucks:
            config.package_order[truck] = self.package_order[truck].copy()
        return config

# random state
def ngasal(isekai: Isekai) -> IsekaiOrder:
    config = IsekaiOrder(isekai)

    for package in isekai.packages:
        kelempar(config, package)

    for truck in isekai.trucks:
        config.package_order[truck] = []
        for package in isekai.packages:
            if config.get_package_truck(package) is truck:
                config.package_order[truck].append(package)
                if random.random() < 0.25:
                    keguling(config, package)
        random.shuffle(config.package_order[truck])    
        for package in config.package_order[truck]:
            position = config.get_package_position(package)
            position.y = 0
            for other_package in config.package_order[truck]:
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
        for package in config.package_order[truck]:
            if config.get_package_truck(package) is not truck:
                continue
            position = config.get_package_position(package)
            position.y = 0
            for other_package in config.package_order[truck]:
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
def kawin(config1: IsekaiOrder, config2: IsekaiOrder):
    isekai = config1.isekai;
    other_world_1 = config1.copy()
    other_world_2 = config2.copy()

    for truck in isekai.trucks:
        point_of_no_return_1 = random.randint(0, len(config1.package_order[truck]))
        point_of_no_return_2 = random.randint(0, len(config2.package_order[truck]))
        other_world_1.package_order[truck].clear()
        other_world_2.package_order[truck].clear()

        for i in range(0, point_of_no_return_1):
            other_world_1.package_order[truck].append(config1.package_order[truck][i])
        for i in range(0, point_of_no_return_2):
            other_world_2.package_order[truck].append(config2.package_order[truck][i])
        for i in range(point_of_no_return_1, len(config1.package_order[truck])):
            other_world_2.package_order[truck].append(config1.package_order[truck][i])
        for i in range(point_of_no_return_2, len(config2.package_order[truck])):
            other_world_1.package_order[truck].append(config2.package_order[truck][i])

    return [other_world_1, other_world_2]

# position mutation
def kesenggol(config: IsekaiOrder, package: LovePackage = None):
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
def keguling(config: IsekaiOrder, package: LovePackage = None):
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
def ketukar(config: IsekaiOrder):
    package1 = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]
    package2 = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]
    if package1 is package2:
        return
    truck1 = config.get_package_truck(package1)
    truck2 = config.get_package_truck(package2)
    order1 = config.get_package_order(package1)
    order2 = config.get_package_order(package2)
    position1 = config.get_package_position(package1)
    position2 = config.get_package_position(package2)
    orientation1 = config.get_package_orientation(package1)
    orientation2 = config.get_package_orientation(package2)
    config.configure_package(package1, truck2, position2, orientation2, order2)
    config.configure_package(package2, truck1, position1, orientation1, order1)

# masuk keluar paket dari truck
def kelempar(config: IsekaiOrder, package: LovePackage = None):
    if package is None:
        package = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]
    truck = config.get_package_truck(package)

    if truck is None:
        truck = config.isekai.trucks[random.randint(0, len(config.isekai.trucks) - 1)]
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

# acak urutan
def kejengkang(config: IsekaiOrder, package: LovePackage = None):
    if package is None:
        package = config.isekai.packages[random.randint(0, len(config.isekai.packages) - 1)]

    truck = config.get_package_truck(package)
    if truck is not None:
        order = random.randint(0, len(config.package_order[truck]))
        config.set_package_order(package, order)

    
# mutasi
def kelainan(config: IsekaiOrder):
    match random.randint(0, 4):
        case 0: kesenggol(config)
        case 1: keguling(config)
        case 2: ketukar(config)
        case 3: kelempar(config)
        case 3: kejengkang(config)

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
    avg_value = round(math.sqrt(total_value // len(config.isekai.packages)))

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
def dolan(isekai: Isekai, generation=1000, jumlah_penduduk=100, peluang_kelainan=0.05, persen_kaum_elit=0.05, debug=False) -> dict:
    start_time = time.perf_counter()
    
    orde_lama: list[IsekaiOrder] = []
    for i in range(jumlah_penduduk):
        orde_lama.append(ngasal(isekai))

    the_first_world: IsekaiConfiguration # best initial state
    the_first_kesejahteraan = 0 # best initial value
    the_perfect_world: IsekaiConfiguration # best final state
    the_perfect_kesejahteraan = 0
    list_termiskin = []
    list_termakmur = []
    list_terbiasa = []

    the_perfect_world = IsekaiConfiguration(isekai)
    the_perfect_kesejahteraan = 0
    kesejahteraan_rakyat = dict[IsekaiOrder, int]()

    for i in range(generation):
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
                the_perfect_world = rakyat
            if first:
                first = False
                termiskin = ks
                termakmur = ks
            else:
                termiskin = min(termiskin, ks)
                termakmur = max(termakmur, ks)
        terbiasa = total_kesejahteraan / jumlah_penduduk
        
        if i == 0:
            the_first_world = the_perfect_world
            the_first_kesejahteraan = the_perfect_kesejahteraan
    
        list_termiskin.append(termiskin)
        list_termakmur.append(termakmur)
        list_terbiasa.append(terbiasa) 

        if debug:
            print(f"Generation {i}:")
            print(f" -> termakmur =", termakmur)
            print(f" -> terbiasa =", terbiasa)
            print(f" -> termiskin =", termiskin)
            print(f" -> varietas =", len(kesejahteraan_rakyat))

        termiskin_lama = termiskin
        if termiskin_lama <= 0:
            total_kesejahteraan += (-termiskin_lama + 1) * jumlah_penduduk

        orde_baru = []
        first = True
        for _ in range(jumlah_penduduk):
            rakyat1: IsekaiConfiguration
            rakyat2: IsekaiConfiguration

            random_pilih1 = random.randint(0, total_kesejahteraan - 1)
            random_pilih2 = random.randint(0, total_kesejahteraan - 1)
            for rakyat in orde_lama:
                if random_pilih1 < kesejahteraan_rakyat[rakyat] + max(0, -termiskin_lama + 1):
                    rakyat1 = rakyat
                    break
                random_pilih1 -= kesejahteraan_rakyat[rakyat] + max(0, -termiskin_lama + 1)
            for rakyat in orde_lama:
                if random_pilih2 < kesejahteraan_rakyat[rakyat] + max(0, -termiskin_lama + 1):
                    rakyat2 = rakyat
                    break
                random_pilih2 -= kesejahteraan_rakyat[rakyat] + max(0, -termiskin_lama + 1)

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
            total_kesejahteraan += (-termiskin_lama + 1) * (2 * jumlah_penduduk)
        elif termiskin_baru <= 0:
            total_kesejahteraan += (-termiskin_baru + 1) * (3 * jumlah_penduduk) - (-termiskin_lama + 1) * jumlah_penduduk
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

        for rakyat, ks in kesejahteraan_rakyat.items():
            if ks > the_perfect_kesejahteraan and rakyat.is_valid():
                the_perfect_world = rakyat

        rakyat_mati = []
        for rakyat in kesejahteraan_rakyat.keys():
            if rakyat not in orde_terbaru:
                rakyat_mati.append(rakyat)

        for rakyat in rakyat_mati:
            kesejahteraan_rakyat.pop(rakyat)
    
        orde_lama = orde_terbaru

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
            the_perfect_world = rakyat
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
        "max_value_history": list_termakmur,
        "avg_value_history": list_terbiasa,
        "min_value_history": list_termiskin,
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