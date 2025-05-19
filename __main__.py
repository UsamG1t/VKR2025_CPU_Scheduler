from algo1 import Algo1
from algo2 import Algo2
from objects import Task, CPU

from fractions import Fraction
from itertools import product
from copy import deepcopy
import random

### Точечные эксперименты с конкретными данными
def one_exp():
    count = 20
    task_count = 25
    dl = 1
    speed = 100
    min_speed = 50
    static_p = 10

    def base_fast(task_set: list[Task], deadline: int, cpu_count: int):
        cpu = CPU(0, speed, min_speed, Fraction(static_p,100))
        base_energy = deadline * cpu.system_consumption * cpu_count
        for task in task_set:
            base_energy += task.cycles * task.real_cycles_coef * task.energy_coef * (cpu.speed)**2
            
        print(base_energy)
        return base_energy


    random.seed(421)
    cpu_set = [CPU(i, speed, min_speed, Fraction(static_p, 100)) for i in range(count)]
    task_cycles = [random.randint(1, 100) for i in range(task_count)]
    task_set = [Task(i, task_cycles[i], Fraction(7, 10), 1) for i in range(task_count)]
    deadline = dl * sum(task_cycles) // (count * cpu_set[0].speed) + (dl * sum(task_cycles) % (count * cpu_set[0].speed) > 0)

    print(task_cycles, dl * sum(task_cycles), deadline)

    base = base_fast(task_set, deadline, len(cpu_set))

    cpu1, tasks1 = deepcopy(cpu_set), deepcopy(task_set)
    cpu2, tasks2 = deepcopy(cpu_set), deepcopy(task_set)
    cpu3, tasks3 = deepcopy(cpu_set), deepcopy(task_set)
    cpu4, tasks4 = deepcopy(cpu_set), deepcopy(task_set)

    NoMigNoDPM = Algo1(tasks1, deadline, cpu1)
    MigNoDPM = Algo1(tasks2, deadline, cpu2)
    NoMigDPM = Algo2(tasks3, deadline, cpu3)
    MigDPM = Algo1(tasks4, deadline, cpu4)

    NoMigNoDPM.NoMigrationAlgo()
    NoMigNoDPM.show_schedule()
    print(NoMigNoDPM.get_energy() / base * 100)

    MigNoDPM.MigrationAlgo()
    MigNoDPM.show_schedule()
    print(MigNoDPM.get_energy() / base * 100)

    NoMigDPM.NoMigrationAlgo()
    NoMigDPM.show_schedule()
    print(NoMigDPM.get_energy() / base * 100)

    MigDPM.NewDPMMigrationAlgo()
    MigDPM.show_schedule()
    print(MigDPM.get_energy() / base * 100)

# one_exp()
###


###Основной код

CPU_count = [2, 5, 10, 20]
CPU_min_speed = [50, 25, 10]
static_P_percent = [(Fraction(0, 100), 0), (Fraction(1, 100), 1) , (Fraction(5, 100), 2), (Fraction(10, 100), 3), (Fraction(20, 100), 4)]
TASK_count = [10, 25, 50, 75, 100]
Deadlines = [1, 2, 4]


def random_coef(a):
    return 7 * (a % 4 == 0) + 8 * (a % 4 == 1) + 9 * (a % 4 == 2) + 10 * (a % 4 == 3)

def testing():
    for count, min_speed, static_p_percent in product(CPU_count, CPU_min_speed, static_P_percent):
        cpu_set = [CPU(i, 100, min_speed, static_p_percent[0]) for i in range(count)]

        with open(f"VKR_results/Experiment_{count}_{min_speed}_{static_p_percent[1]}.csv", "w+") as csv:
        
            for task_count, dl in product(TASK_count, Deadlines):
                random.seed(421)
                task_cycles = [random.randint(1, 100) for i in range(task_count)]
                task_set = [Task(i, task_cycles[i], Fraction(random_coef(task_cycles[i]), 10), 1) for i in range(task_count)]
                deadline = dl * sum(task_cycles) // (count * cpu_set[0].speed) + (dl * sum(task_cycles) % (count * cpu_set[0].speed) > 0)
                
                energies = []

                cpu1, tasks1 = deepcopy(cpu_set), deepcopy(task_set)
                cpu2, tasks2 = deepcopy(cpu_set), deepcopy(task_set)
                cpu3, tasks3 = deepcopy(cpu_set), deepcopy(task_set)
                cpu4, tasks4 = deepcopy(cpu_set), deepcopy(task_set)

                NoMigNoDPM = Algo1(tasks1, deadline, cpu1)
                MigNoDPM = Algo1(tasks2, deadline, cpu2)
                NoMigDPM = Algo2(tasks3, deadline, cpu3)
                MigDPM = Algo1(tasks4, deadline, cpu4)

                NoMigNoDPM.NoMigrationAlgo()
                NoMigNoDPM.show_schedule()
                energies.append(NoMigNoDPM.get_energy())
        
                MigNoDPM.MigrationAlgo()
                MigNoDPM.show_schedule()
                energies.append(MigNoDPM.get_energy())
        
                NoMigDPM.NoMigrationAlgo()
                NoMigDPM.show_schedule()
                energies.append(NoMigDPM.get_energy())
        
                MigDPM.NewDPMMigrationAlgo()
                MigDPM.show_schedule()
                energies.append(MigDPM.get_energy())
        
                print(",".join(map(str, [task_count, dl /count ] + energies)), end="\n", file=csv)

testing()

def base_energy():
    for count, static_p_percent in product(CPU_count, static_P_percent):
        with open(f"VKR_results/BaseData_{count}_{static_p_percent[1]}.csv", "w+") as csv:
        
            cpu = CPU(0, 100, 100, static_p_percent[0])
            for task_count, dl in product(TASK_count, Deadlines):
                random.seed(421)
                task_cycles = [random.randint(1, 100) for i in range(task_count)]
                task_set = [Task(i, task_cycles[i], Fraction(random_coef(task_cycles[i]), 10), 1) for i in range(task_count)]
                deadline = dl * sum(task_cycles) // (count * cpu.speed) + (dl * sum(task_cycles) % (count * cpu.speed) > 0)
                
                base_energy = deadline * cpu.system_consumption * count
                for task in task_set:
                    base_energy += task.cycles * task.real_cycles_coef * task.energy_coef * (cpu.speed)**2
                    
                print(",".join(map(str, [task_count, dl / count, base_energy])), end="\n", file=csv)

base_energy()