from fractions import Fraction
from objects import Task, CPU, Queue_item
from copy import deepcopy

class Algo1:
    def __init__(self, T: list[Task], D: int, M: list[CPU]):
        self.T = T
        self.D = D
        self.M = M


    def NoMigrationAlgo(self):
        self.T.sort(reverse=True)

        CPU_cycles = [0 for i in range(len(self.M))]
        CPU_tasks = [[] for i in range(len(self.M))]

        for task in self.T:
            p_min = min(CPU_cycles)
            pos = CPU_cycles.index(p_min)
            CPU_tasks[pos].append(task)
            CPU_cycles[pos] += task.cycles

        
        for cpu in self.M:
            cpu_speed = max(min([Fraction(CPU_cycles[cpu.id], self.D), Fraction(cpu.speed)]), Fraction(cpu.min_speed))
            for task in CPU_tasks[cpu.id]:
                cpu.queue.append(Queue_item(task, cpu_speed))
                task.partition[1] = [cpu.id, task.cycles]

            if not cpu.correct_schedule(self.D):
                print(f"Uncorrect schedule on CPU_{cpu.id}")
                cpu.show_cpu_schedule()
                return None
        return self

############
  
    def MigrationAlgo(self):
        self.T.sort(reverse=True)

        C = sum(task.cycles for task in self.T)
        M_CPU = len(self.M)

        if (C / (M_CPU * self.D) > max(cpu.speed for cpu in self.M) or 
            max(task.cycles / self.D for task in self.T) > max(cpu.speed for cpu in self.M)):
            print("Feasible schedule is not exists!")
            return None
        
        i = 0
        
        # NoMigrationTasks
        while i < len(self.T):
            if self.T[i].cycles > (C / M_CPU):
                cpu_speed = max(min([Fraction(self.T[i].cycles, self.D), Fraction(self.M[M_CPU-1].speed)]), Fraction(self.M[M_CPU-1].min_speed))
                self.M[M_CPU-1].queue.append(Queue_item(self.T[i], cpu_speed, execution_time=Fraction(self.T[i].cycles, cpu_speed), start_time=0))
                self.T[i].partition[1] = [self.M[M_CPU-1].id, self.T[i].cycles]
            
                C -= self.T[i].cycles
                i += 1
                M_CPU -= 1
            else:
                break


        S = max(Fraction(C, M_CPU * self.D), Fraction(self.M[M_CPU-1].min_speed))
        t = 0        
        
        # MigrationTasks
        while i < len(self.T):
            if t + Fraction(self.T[i].cycles, S) > self.D:
                
                task_execution_time = t + Fraction(self.T[i].cycles, S) - self.D
                self.M[M_CPU-2].queue.append(Queue_item(self.T[i], S, execution_time=task_execution_time, start_time=0, task_part=1))
                self.T[i].partition[1] = [self.M[M_CPU-2].id, S * task_execution_time]

                task_execution_time = self.D - t
                self.M[M_CPU-1].queue.append(Queue_item(self.T[i], S, execution_time=task_execution_time, start_time=t, task_part=2))
                self.T[i].partition[2] = [self.M[M_CPU-1].id, S * task_execution_time]

                M_CPU -= 1
            
            else:
                task_execution_time = Fraction(self.T[i].cycles, S)
                self.M[M_CPU-1].queue.append(Queue_item(self.T[i], S, execution_time=task_execution_time, start_time=t, task_part=1))
                self.T[i].partition[1] = [self.M[M_CPU-1].id, self.T[i].cycles]
            
            t = (t + self.T[i].cycles / S) % self.D
            i += 1

        for cpu in self.M:
            if not cpu.correct_schedule(self.D):
                print(f"Uncorrect schedule on CPU_{cpu.id}")
                cpu.show_cpu_schedule()
                return None
            
        return self

############

    def NewDPMMigrationAlgo(self):
        self.T.sort(reverse=True)

        C = sum(task.cycles for task in self.T)
        M_CPU = len(self.M)

        if (C / (M_CPU * self.D) > max(cpu.speed for cpu in self.M) or 
            max(task.cycles / self.D for task in self.T) > max(cpu.speed for cpu in self.M)):
            print("Feasible schedule is not exists!")
            return None
        
        i = 0
        
        # NoMigrationTasks
        while i < len(self.T):
            if self.T[i].cycles > (C / M_CPU):
                cpu_speed = Fraction(self.M[M_CPU-1].speed)
                self.M[M_CPU-1].queue.append(Queue_item(self.T[i], cpu_speed, execution_time=Fraction(self.T[i].cycles, cpu_speed), start_time=0))
                self.T[i].partition[1] = [self.M[M_CPU-1].id, self.T[i].cycles]
            
                C -= self.T[i].cycles
                i += 1
                M_CPU -= 1
            else:
                break


        S = Fraction(C, M_CPU * self.D)
        t = 0        
        # MigrationTasks
        while i < len(self.T):
            if t + Fraction(self.T[i].cycles, S) > self.D:
                
                part1 = (t + Fraction(self.T[i].cycles, S) - self.D) * S
                part2 = (self.D - t) * S

                self.M[M_CPU-2].queue.append(Queue_item(self.T[i], self.M[M_CPU-2].speed, execution_time=Fraction(part1, self.M[M_CPU-2].speed), start_time=0, task_part=1))
                self.T[i].partition[1] = [self.M[M_CPU-2].id, part1]

                self.M[M_CPU-1].queue.append(Queue_item(self.T[i], self.M[M_CPU-1].speed, execution_time=Fraction(part2, self.M[M_CPU-1].speed), start_time=t, task_part=2))
                self.T[i].partition[2] = [self.M[M_CPU-1].id, part2]

                M_CPU -= 1
            
            else:
                task_execution_time = Fraction(self.T[i].cycles, self.M[M_CPU-1].speed)
                self.M[M_CPU-1].queue.append(Queue_item(self.T[i], self.M[M_CPU-1].speed, execution_time=task_execution_time, start_time=t, task_part=1))
                self.T[i].partition[1] = [self.M[M_CPU-1].id, self.T[i].cycles]
            
            t = (t + Fraction(self.T[i].cycles, S)) % self.D
            i += 1

        for cpu in self.M:
            last_item = cpu.queue[-1] if len(cpu.queue) else Queue_item(None, None, 0, 0, 1)
            this_start_time = last_item.start_time + last_item.execution_time
            sleep_task = Task('slp', cpu.speed * (self.D - this_start_time), 1, -Fraction(cpu.system_consumption, cpu.speed**3))
            cpu.queue.append(Queue_item(sleep_task, cpu_execution_speed=cpu.speed, execution_time=self.D - this_start_time, start_time=this_start_time))
            sleep_task.partition[1] = [cpu.id, cpu.speed * ((self.D - this_start_time))]
        
        for cpu in self.M:
            if not cpu.correct_schedule(self.D):
                print(f"Uncorrect schedule on CPU_{cpu.id}")
                cpu.show_cpu_schedule()
                return None
            
        return self

###################################

    def show_schedule(self, filename=None):
        full_energy = 0
        for cpu in self.M:
            cpu.show_cpu_schedule(filename)
            print(f"CPU{cpu.id} energy: {cpu.Total_energy()}\n")

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