import random
import time
import os
import threading as th
import winsound

# -----------------------------------
# Colors
# -----------------------------------
# Enable ANSI escape codes on Windows (for color support)
os.system('')

# Color constants
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"

# -----------------------------------
# Time and Efficiency
# -----------------------------------
efficiency = 0.8
def calculate_work_break_times():
    
    # Calculate rest time: max(5, (1 / efficiency - 1) * 20)
    rest_time = max(5, (1 / efficiency - 1) * 20)
    
    # Calculate work time: rest_time * (efficiency / (1 - efficiency))
    work_time = rest_time * (efficiency / (1 - efficiency))
    
    return work_time, rest_time

def getWorkTime():
    """
    Get the work time based on the efficiency.
    
    Returns:
        float: The calculated work time in minutes.
    """
    work_time, _ = calculate_work_break_times()
    return work_time

def getBreakTime():
    """
    Get the break time based on the efficiency.
    
    Returns:
        float: The calculated break time in minutes.
    """
    _, break_time = calculate_work_break_times()
    return break_time
 

# -----------------------------------
# Tasks File
# -----------------------------------

def get_task_name(line):
    parts = line.split(" ")
    res = parts[:-1]
    return (" ".join(res)).strip()

def get_task_imp(line):
    return float(line.split(" ")[-1])

taskFName = os.path.dirname(os.path.abspath(__file__))+ "/tasks.txt"
def GetFile():
    if os.path.exists(taskFName):
        task_f = open(taskFName, "r")
    else:
        task_f = open(taskFName, "w+")
    return task_f
    
importances = dict()
progress = dict()
def get_task():
    task_f = GetFile()
    tasks = task_f.readlines()
    task_f.close()
    
    global importances
    global progress
    importances.clear()
    n_progress = dict()
    
    for task in tasks:
        n_progress[get_task_name(task)] = progress[get_task_name(task)] if get_task_name(task) in progress else 0
        importances[get_task_name(task)] = get_task_imp(task)
        
    progress = n_progress
    return tasks

def add_t(name, importance):
    task_f = GetFile()
    task_f.write(f"\n{name} {importance}")
    task_f.close()


# -----------------------------------
# Timer File
# -----------------------------------

start_time = None
time_interval = 0

paused = False
sThread = None

break_time = 0
quit = False

def start(mins):
    global start_time
    global paused
    global sThread
    
    if paused:
        paused = False
    else:
        global time_interval
        time_interval = mins * 60
    
    if start_time == None:
        start_time = time.time()
        sThread = th.Thread(target=timing_loop)
        sThread.start()

def diff(tp):
    if tp is None:
        return 0
    return time.time() - tp

def pause():
    global paused
    global time_interval
    global start_time
    global sThread
    if paused:
        print(f"{YELLOW}Timing is already paused.{RESET}")
        return
    if start_time == None:
        print(f"{RED}Timing has not started yet.{RESET}")
        return
    time_interval -= diff(start_time)
    start_time = None
    paused = True
    if sThread is not None:
        sThread.join()
        sThread = None
    

def timing_loop():
    while not quit and start_time != None and not paused:
        if diff(start_time) >= time_interval:
            while not quit and start_time != None:
                time.sleep(1)
                winsound.Beep(1000, 1000)
                print(f"\n{GREEN}Time is up!{RESET}\n{MAGENTA}> {RESET}", end="")
            break
        time.sleep(0.25)

def reset():
    global start_time
    global time_interval
    global paused
    global pause_start
    global paused_time
    global sThread
    start_time = None
    time_interval = 0
    paused = False
    if sThread is not None:
        sThread.join()
        sThread = None

# -----------------------------------
# Next Task
# -----------------------------------
def next_task():
    tasks = get_min_keys(progress)
    if len(tasks) == 0:
        print(f"{RED}No tasks available.{RESET}")
        return None
    task = random.choice(tasks)
    return task

def get_min_keys(d: dict[str, int]) -> list[str]:
    if not d:
        return []
    
    min_value = min(d.values())
    min_keys = [key for key, value in d.items() if value == min_value]
    
    return min_keys

def do(task):
    if task is None:
        print(f"{RED}No task to do.{RESET}")
        return
    
    print(f"{GREEN}Doing task: {task} with importance {importances[task]}{RESET}")
    
    wt, bt = calculate_work_break_times()
    print(f"{YELLOW}Work time {wt:.1f} minutes, Break time {bt:.1f} minutes{RESET}")
    
    if input(f"{BLUE}continue? (y/n): {RESET}").strip().lower() != 'n':
        start(wt)
        global break_time
        break_time += bt
        progress[task] += 1 / importances[task]
    
get_task()
print(f"{CYAN}h for help menu{RESET}")
ui = ""
while ui != "q":
    ui = input(f"{MAGENTA}> {RESET}")
    words = ui.strip().split()
    if ui == "":
        continue
    cmd = words[0]
    match cmd:
        case "a":
            try:
                cmdLen = len(cmd) + 1
                importanceLen = len(words[-1]) +1
                name = ui[cmdLen:-importanceLen]
                importance = words[-1]
                add_t(name, importance)
            except Exception as e:
                print(f"{RED}{e.args} Incorrect format: a for add task e.g. add task 1, add [task name] [importance]{RESET}")
        case "b":
            try:
                if len(words) > 1:
                    start(float(words[1]))
                    print(f"Break started for {words[1]} minutes")
                    break_time -= float(words[1])
                else:
                    start(break_time)
                    break_time = 0
            except Exception as e:
                print(f"{RED}{e.args} Incorrect format: b for break e.g. b 5 for 5 min break{RESET}")
        case "sb":
            try:
                if len(words) > 1:
                    break_time = float(words[1])
                else:
                    _, bt = calculate_work_break_times()
                    break_time = bt
            except Exception as e:
                print(f"{RED}{e.args} Incorrect format: sb for set break time e.g. sb 5 for 5 min break{RESET}")
        case "gb":
            print(f"{CYAN}Break time is set to {break_time:.1f} minutes{RESET}")
        case "gwb":
            work_time, bt = calculate_work_break_times()
            print(f"{CYAN}Default work time: {work_time:.1f} minutes, Break time: {bt:.1f} minutes{RESET}")
        case "c":
            os.system('cls')
            print(f"{CYAN}h for help menu{RESET}")
        case "d":
            if len(words) < 2:
                print(f"{RED}Please specify a task to do.{RESET}")
                continue
            task = " ".join(words[1:])
            if task not in progress:
                print(f"{RED}Task '{task}' not found.{RESET}")
                continue
            if paused:
                print(f"{YELLOW}Timing is paused. Please resume before doing a task.{RESET}")
                continue
            do(task)
        case "dn":
            task = next_task()
            do(task)
        case "e":
            try:
                if "/" in words[1]:
                    num = words[1].split("/")
                    efficiency = float(num[0]) / float(num[1])
                else:
                    efficiency = float(words[1])
            except Exception as e:
                print(f"{RED}{e.args} Incorrect format: e for set efficiency e.g. e 0.5 or e 1/2{RESET}")
        case "ge":
            print(f"{CYAN}Efficiency is set to {efficiency}{RESET}")
        case "ls":
            task = get_task()
            print(f"{BOLD}{BLUE}Tasks:{RESET}")
            for line in task:
                print(f"{BLUE}{line.strip()}{RESET}")
        case "h":
            print(f"{BOLD}{CYAN}a for add task e.g. add task 1, add [task name] [importance]{RESET}")
            print(f"{CYAN}b for break e.g. b 5 for 5 min break{RESET}")
            print(f"{CYAN}sb for set break time e.g. sb 5 for 5 min break{RESET}")
            print(f"{CYAN}gb for get break time{RESET}")
            print(f"{CYAN}gwb for get default work and break time{RESET}")
            print(f"{CYAN}c for clear{RESET}")
            print(f"{CYAN}d for do task e.g. d task1{RESET}")
            print(f"{CYAN}dn for do next task with minimum progress{RESET}")
            print(f"{CYAN}e for set efficiency e.g. e 0.5 or e 1/2{RESET}")
            print(f"{CYAN}ge for get efficiency{RESET}")
            print(f"{CYAN}ls for list of tasks and their importance (also refreshes internal task lists){RESET}")
            print(f"{CYAN}h for help menu{RESET}")
            print(f"{CYAN}n for next task{RESET}")
            print(f"{CYAN}p for pause timing{RESET}")
            print(f"{CYAN}gp for get progress{RESET}")
            print(f"{CYAN}q for quit{RESET}")
            print(f"{CYAN}r for reset timing{RESET}")
            print(f"{CYAN}tl for time left{RESET}")
            print(f"{CYAN}s for start or restart timing e.g. s 5 for 5 min work time default to work time calculated by efficiency{RESET}")
        case "n":
            task = next_task()
            print(f"{GREEN}Next task: '{task}' with importance {importances[task]}{RESET}")
        case "p":
            pause()
        case "gp":
            print(f"{CYAN}Progress:{RESET}")
            for task, prog in progress.items():
                print(f"{GREEN} - {task}: {prog:.1f}{RESET}")
        case "q":
            quit = True
            break
        case "r":
            reset()
        case "tl":
            if paused:
                print(f"{CYAN}Time left: {int(time_interval // 60)} min {time_interval % 60:.1f} seconds{RESET}")
                continue
            d = diff(start_time)
            sec = time_interval - d
            if sec < 0:
                sec = 0
            print(f"{CYAN}Time left: {int(sec // 60)} min {sec % 60:.1f} seconds{RESET}")
        case "s":
            try:
                if len(words) > 1:
                    start(float(words[1]))
                    break_time += float(words[1]) * (1-efficiency) / efficiency
                else:
                    if not paused:
                        break_time += calculate_work_break_times()[1]
                    start(calculate_work_break_times()[0])
            except Exception as e:
                print(f"{RED}{e.args} Incorrect format: s for start or restart timing e.g. s 5 for 5 min work time{RESET}")