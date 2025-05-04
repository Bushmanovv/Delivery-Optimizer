import random
from copy import deepcopy
from models import Vehicle, DeliverySolution

def genetic_algorithm(packages, vehicles, population_size=80, mutation_rate=0.05, generations=500):

    # Attempt-limited initial solution generator
    def create_solution(max_attempts=100):
        for _ in range(max_attempts):
            sorted_packages = sorted(packages, key=lambda p: p.priority)
            vehicles_copy = [Vehicle(v.id, v.capacity) for v in vehicles]

            for pkg in sorted_packages:
                random.shuffle(vehicles_copy)
                for v in vehicles_copy:
                    if v.can_add(pkg):
                        v.packages.append(pkg)
                        break

            solution = DeliverySolution(vehicles_copy)
            all_pkgs = {p.id for v in solution.vehicles for p in v.packages}

            if solution.is_valid() and len(all_pkgs) > 0:
                return solution

        raise Exception("Unable to generate valid initial solution after many attempts.")

    # Crossover combines packages from both parents
    def crossover(parent1, parent2):
        vehicle_cap = {v.id: v.capacity for v in parent1.vehicles}
        child_vehicles = [Vehicle(i, vehicle_cap[i]) for i in vehicle_cap]

        pkg_map = {}
        for v in parent1.vehicles:
            for p in v.packages:
                pkg_map[p.id] = p
        for v in parent2.vehicles:
            for p in v.packages:
                pkg_map[p.id] = p

        for p in pkg_map.values():
            random.shuffle(child_vehicles)
            for v in child_vehicles:
                if v.can_add(p):
                    v.packages.append(p)
                    break

        return DeliverySolution(child_vehicles)

    # Mutation moves a package from one vehicle to another
    def mutate(sol):
        vlist = sol.vehicles
        v1 = random.choice(vlist)
        if not v1.packages:
            return
        pkg = random.choice(v1.packages)
        v1.packages.remove(pkg)

        other = [v for v in vlist if v != v1 and v.can_add(pkg)]
        if not other:
            v1.packages.append(pkg)
            return
        random.choice(other).packages.append(pkg)

    # Weighted selection based on inverse distance (fitness)
    def pick_parents(pop):
        weights = []
        for sol in pop:
            d = sol.total_distance()
            if d > 0:
                weights.append(1 / d)
            else:
                weights.append(1e-6)
        return random.choices(pop, weights=weights, k=2)

    # === Main Genetic Algorithm Loop ===
    population = [create_solution() for _ in range(population_size)]
    best = min(population, key=lambda sol: sol.total_distance())

    for gen in range(generations):
        new_pop = []
        for _ in range(population_size):
            p1, p2 = pick_parents(population)
            child = crossover(p1, p2)

            if random.random() < mutation_rate:
                mutate(child)

            if child.is_valid() and sum(len(v.packages) for v in child.vehicles) > 0:
                new_pop.append(child)

        # Ensure population is not empty
        if new_pop:
            population = new_pop
        else:
            population = population[:]  # retain previous generation

        # Track the best solution
        best_candidate = min(population, key=lambda sol: sol.total_distance())
        if best_candidate.total_distance() < best.total_distance():
            best = best_candidate

        if gen % 50 == 0:
            print(f"Generation {gen} | Best Distance: {best.total_distance():.2f} km")

    all_assigned_ids = {p.id for v in best.vehicles for p in v.packages}
    all_input_ids = {p.id for p in packages}
    unassigned = all_input_ids - all_assigned_ids
    print(f"️ Unassigned packages: {sorted(unassigned)}")

    return best
