import math
import random
from copy import deepcopy
from models import DeliverySolution, Vehicle

def simulated_annealing(packages, vehicles, initial_temp=1000, cooling_rate=0.95, stopping_temp=1, iterations_per_temp=100):
    
    def make_initial_solution():
        sorted_pkgs = sorted(packages, key=lambda p: p.priority)
        vehicles_copy = [Vehicle(v.id, v.capacity) for v in vehicles]
        
        for pkg in sorted_pkgs:
            random.shuffle(vehicles_copy)
            for v in vehicles_copy:
                if v.can_add(pkg):
                    v.packages.append(pkg)
                    break
        
        return DeliverySolution(vehicles_copy)

    def get_neighbor(sol):
        sol_copy = sol.clone()
        all_pkgs = []
        for vi, v in enumerate(sol_copy.vehicles):
            for idx in range(len(v.packages)):
                all_pkgs.append((vi, idx))

        if not all_pkgs:
            return sol_copy

        vi_from, pkg_idx = random.choice(all_pkgs)
        pkg = sol_copy.vehicles[vi_from].packages.pop(pkg_idx)

        other_vs = [v for i, v in enumerate(sol_copy.vehicles) if i != vi_from and v.can_add(pkg)]
        if not other_vs:
            sol_copy.vehicles[vi_from].packages.append(pkg)
            return sol_copy

        random.choice(other_vs).packages.append(pkg)
        return sol_copy

    def prob_accept(current_cost, new_cost, temp):
        if new_cost < current_cost:
            return 1.0
        else:
            return math.exp(-(new_cost - current_cost) / temp)

    current_sol = make_initial_solution()
    best_sol = current_sol.clone()
    temp = initial_temp

    while temp > stopping_temp:
        for _ in range(iterations_per_temp):
            neighbor_sol = get_neighbor(current_sol)

            if not neighbor_sol.is_valid():
                continue

            if prob_accept(current_sol.total_distance(), neighbor_sol.total_distance(), temp) > random.random():
                current_sol = neighbor_sol
                if current_sol.total_distance() < best_sol.total_distance():
                    best_sol = current_sol

        temp = temp * cooling_rate

    return best_sol
