from fractions import Fraction
from objects import Task, CPU, Queue_item


class Algo2:
    def __init__(self, T: list[Task], D: int, M: list[CPU]):
        self.T = T
        self.D = D
        self.M = M

    def MES(self, schedule: list[tuple[list[Task], int]]):
        CPU_cycles: list[int] = [0] + [x[1] for x in schedule] #self.M + 1

        L = CPU_cycles[-1]
        t = [0 for i in range(len(CPU_cycles))] # self.M + 1
        s = [0 for i in range(len(CPU_cycles))] # self.M + 1
        
        for i in range(1, len(CPU_cycles)):
            s[i] =  CPU_cycles[i] - CPU_cycles[i-1] # cycles, NOT SPEED
            t[i] = t[i-1] + self.D * Fraction( (CPU_cycles[i] - CPU_cycles[i-1]) , L)
            if ((CPU_cycles[i] - CPU_cycles[i-1]) < 0):
                raise TypeError

        for cpu, task_set in zip(self.M, schedule):
            task_set = task_set[0]
            part = 1
            section = 1
            total_cycles_for_cpu = 0
            
            for task in task_set:
                remaining_cycles = task.cycles
                while total_cycles_for_cpu + remaining_cycles > CPU_cycles[section]:
                    if t[section] - t[section - 1] == 0 or s[section] == 0:
                        section += 1
                        continue
                    cpu_speed = max(min(Fraction(s[section], (t[section] - t[section - 1])), Fraction(cpu.speed, 1)), Fraction(cpu.min_speed, 1))
                    cpu.queue.append(Queue_item(task, cpu_execution_speed=cpu_speed, execution_time=None, start_time=None, task_part=part))
                    task.partition[part] = [cpu.id, Fraction(CPU_cycles[section] - total_cycles_for_cpu)]
                    remaining_cycles -= CPU_cycles[section] - total_cycles_for_cpu
                    total_cycles_for_cpu = CPU_cycles[section]
                    part += 1
                    section += 1
                
                cpu_speed = max(min(Fraction(s[section], (t[section] - t[section - 1])), Fraction(cpu.speed, 1)), Fraction(cpu.min_speed, 1))
                cpu.queue.append(Queue_item(task, cpu_execution_speed=cpu_speed, execution_time=None, start_time=None, task_part=part))
                task.partition[part] = [cpu.id, remaining_cycles]
                total_cycles_for_cpu += remaining_cycles
                if total_cycles_for_cpu == CPU_cycles[section]:
                    section += 1
                part = 1

            if section < len(t):
                sleep_task = Task('slp', cpu.speed * (self.D - t[section]), Fraction(1), -Fraction(cpu.system_consumption, cpu.speed**3))
                cpu.queue.append(Queue_item(sleep_task, cpu_execution_speed=cpu.speed, execution_time=self.D - t[section], start_time=t[section]))
                sleep_task.partition[1] = [cpu.id, cpu.speed * (self.D - t[section])]

        for cpu in self.M:
            if not cpu.correct_schedule(self.D):
                print(f"Uncorrect schedule on CPU_{cpu.id}")
                cpu.show_cpu_schedule()
                return None
            
        return self

    def NoMigrationAlgo(self):
        self.T.sort(reverse=True)
        
        CPU_cycles = [0 for i in range(len(self.M))]
        CPU_tasks = [[] for i in range(len(self.M))]
        
        for task in self.T:
            p_min = min(CPU_cycles)
            pos = CPU_cycles.index(p_min)
            CPU_tasks[pos].append(task)
            CPU_cycles[pos] += task.cycles

        schedule: list[tuple[list[Task], int]] = [(CPU_tasks[i], CPU_cycles[i]) for i in range(len(self.M))]
        schedule.sort(key= lambda x: x[1])

        return self.MES(schedule)
        
    def show_schedule(self, filename=None):
        full_energy = 0
        for cpu in self.M:
            cpu.show_cpu_schedule(filename)
            print(f"CPU energy: {cpu.Total_energy()}\n")

            if full_energy is not None and isinstance(cpu.Total_energy(), float):
                full_energy += cpu.Total_energy()
            else:
                full_energy = None
        if filename:
            print(f"Total energy: {full_energy}", file=filename)
        else:
            print(f"Total energy: {full_energy}")

    def get_energy(self):
        full_enegry = 0
        for cpu in self.M:
            full_enegry += cpu.Total_energy()
        return full_enegry