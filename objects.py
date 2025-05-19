from fractions import Fraction
from math import isclose


class Task:
    def __init__(self, task_num: int, cycles_volume: int, real_cycles_coef: Fraction, energy_coef: Fraction):
        self.id = task_num
        self.cycles = cycles_volume
        self.real_cycles_coef = real_cycles_coef
        self.energy_coef = energy_coef
        self.partition: dict[int, list[int,int]]= {} # dict[task_part: int, list(CPU_id: int, cycles: int)]

    def __lt__(self, other) -> bool:
        return (self.cycles < other.cycles)
    

class Queue_item:
    def __init__(self, t: Task, cpu_execution_speed: Fraction, execution_time: Fraction = None, start_time: Fraction = None, task_part: int = 1):
        self.task = t
        self.cpu_execution_speed = cpu_execution_speed
        self.execution_time = execution_time
        self.start_time = start_time
        self.task_part = task_part
        self.print_energy = 0
class CPU:
    def __init__(self, id: int, speed: int, min_speed: int, system_consumption_percent: Fraction = 0):
        self.id = id
        self.speed = speed
        self.min_speed = min_speed
        
        self.system_consumption = self.speed**3 * system_consumption_percent
        self.total_energy = None
        self.queue: list[Queue_item] = [] # List(Queue_item)

    def Total_energy(self) -> float:
        if self.total_energy is None:
            print("Schedule is not correct or is not fully created!")
            return -1
        return float(self.total_energy)

    def energy_power(self, item: Queue_item) -> Fraction:
        return item.task.energy_coef * (item.cpu_execution_speed)**3
        
    def correct_schedule(self, D: int) -> bool:
        self.queue.sort(key= lambda x: x.start_time if x.start_time else 0)
        
        current_time = Fraction(0)
        del_queue_items = []
        for item in self.queue:        
            if item.start_time != None:
                current_time = item.start_time
            else:
                item.start_time = current_time

            if item.task.partition[item.task_part][1] == 0:
                del_queue_items.append(item)

            exec_time = Fraction(item.task.partition[item.task_part][1], (item.cpu_execution_speed))
            if not item.execution_time:
                item.execution_time = exec_time
            
            current_time += item.execution_time
        
        for item in del_queue_items:
            self.queue.remove(item)

        if current_time > D and not isclose(current_time, D):
            back_time = D
            solved = False

            for item in self.queue[::-1]:
                if Fraction(item.cpu_execution_speed * item.execution_time, back_time - item.start_time) <= self.speed:
                    item.cpu_execution_speed = Fraction(item.cpu_execution_speed * (item.execution_time), back_time - item.start_time)
                    item.execution_time = back_time - item.start_time
                    solved = True
                    break
                else:
                    item.execution_time = Fraction(item.cpu_execution_speed * (exec_time), self.speed)
                    item.start_time = back_time - item.execution_time
                    item.cpu_execution_speed = self.speed
                    back_time = item.start_time
            if not solved:
                return False
            
        return self.slack_reclaiming(D)
    

    def slack_reclaiming(self, D: int) -> bool:
        current_time = 0
        local_total_energy = 0

        for i in range(len(self.queue)):
            cur_item = self.queue[i]
            if cur_item.task.id == 'slp':
                cur_item.task.partition[cur_item.task_part][1] = self.speed * (D - current_time)
                cur_item.start_time = current_time
                cur_item.execution_time = D - current_time
                
            elif current_time < cur_item.start_time:
                potential_speed = Fraction(cur_item.task.partition[cur_item.task_part][1], cur_item.execution_time + (cur_item.start_time - current_time))
                
                if potential_speed >= self.min_speed:
                    cur_item.cpu_execution_speed = potential_speed
                    cur_item.start_time = current_time
                    cur_item.execution_time += (cur_item.start_time - current_time)
                else:
                    time_lag = cur_item.task.cycles * (Fraction(1, self.min_speed) - Fraction(1, cur_item.cpu_execution_speed))
                    lost_time_lag = (cur_item.start_time - current_time) - time_lag
                    
                    cur_item.start_time = current_time
                    cur_item.cpu_execution_speed = self.min_speed
                    cur_item.execution_time = Fraction(cur_item.task.partition[cur_item.task_part][1], self.min_speed)
                    

                    for j in range(i+1, len(self.queue)):
                        self.queue[j].start_time -= lost_time_lag
            
            #Real cycles slack
            cur_item.execution_time *= cur_item.task.real_cycles_coef
            cur_item.print_energy += ( self.system_consumption + self.energy_power(cur_item) ) * cur_item.execution_time
            local_total_energy += cur_item.print_energy
            current_time += cur_item.execution_time

        local_total_energy += self.system_consumption * (D - current_time)
        self.total_energy = local_total_energy
        return True

    def show_cpu_schedule(self, filename=None):
        if filename:
            print(f"CPU {self.id}:", file=filename)

            for item in self.queue:
                print(f'\tTask {item.task.id: >3}: Speed ({float(item.cpu_execution_speed): >3}) / {self.speed: >3} | Part {item.task_part}, {float(item.task.partition[item.task_part][1] * item.task.real_cycles_coef): >3}/{float(item.task.cycles * item.task.real_cycles_coef): >3} | {float(item.start_time)} -> {float(item.start_time + item.execution_time)}', file=filename)
        else:
            print(f"CPU {self.id}:")

            for item in self.queue:
                print(f'\tTask {item.task.id: >3}: Speed ({float(item.cpu_execution_speed): >3}) / {self.speed: >3} | Part {item.task_part}, {float(item.task.partition[item.task_part][1] * item.task.real_cycles_coef): >3}/{float(item.task.cycles * item.task.real_cycles_coef): >3} | {float(item.start_time)} -> {float(item.start_time + item.execution_time)} | {item.print_energy} J')
