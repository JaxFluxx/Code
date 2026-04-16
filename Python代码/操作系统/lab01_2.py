import multiprocessing
import time
import random

# 共享变量：记录当前可用加油枪数量
AVAILABLE_PUMPS = multiprocessing.Value('i', 3)  # 设定 3 个加油枪
mutex = multiprocessing.Lock()  # 互斥锁，确保共享变量操作安全
sem = multiprocessing.Semaphore(3)  # 信号量，最多 3 辆车同时加油

def car_process(car_id):
    while True:
        time.sleep(random.uniform(1, 5))  # 模拟汽车到达的时间间隔
        print(f"🚗 汽车 {car_id} 到达加油站，等待加油枪...")

        sem.acquire()  # 申请加油枪
        mutex.acquire()  # 修改共享变量前上锁
        with AVAILABLE_PUMPS.get_lock():
            AVAILABLE_PUMPS.value -= 1
        mutex.release()

        print(f"⛽ 汽车 {car_id} 开始加油...（剩余加油枪: {AVAILABLE_PUMPS.value}）")
        time.sleep(random.uniform(3, 7))  # 模拟加油时间

        # 释放资源
        mutex.acquire()
        with AVAILABLE_PUMPS.get_lock():
            AVAILABLE_PUMPS.value += 1
        mutex.release()
        sem.release()  # 归还加油枪

        print(f"✅ 汽车 {car_id} 加油完成，离开加油站。（可用加油枪: {AVAILABLE_PUMPS.value}）")

if __name__ == "__main__":
    car_count = 5  # 创建 5 个汽车进程
    car_processes = []

    for i in range(car_count):
        p = multiprocessing.Process(target=car_process, args=(i,))
        car_processes.append(p)
        p.start()

    for p in car_processes:
        p.join()  # 等待所有进程完成
