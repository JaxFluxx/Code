import threading
import time
import random

# 互斥锁（用于保护 reader_count 变量）
reader_count_lock = threading.Lock()

# 读写者同步信号量
room_empty = threading.Semaphore(1)  # 写者独占资源
reader_count = 0  # 当前读者数量


def reader(reader_id):
    global reader_count
    while True:
        time.sleep(random.uniform(1, 3))  # 模拟读者自身工作

        # 申请读
        reader_count_lock.acquire()
        global reader_count
        if reader_count == 0:
            room_empty.acquire()  # 第一个读者进入时锁住写者
        reader_count += 1
        reader_count_lock.release()

        # 读操作
        print(f"📖 读者 {reader_id} 开始阅读...")
        time.sleep(random.uniform(2, 4))  # 模拟阅读时间

        # 读完释放资源
        reader_count_lock.acquire()
        reader_count -= 1
        if reader_count == 0:
            room_empty.release()  # 最后一个读者离开时释放写者
        reader_count_lock.release()

        print(f"✅ 读者 {reader_id} 完成阅读，离开。")


def writer(writer_id):
    while True:
        time.sleep(random.uniform(2, 5))  # 模拟写者自身工作

        # 申请写
        room_empty.acquire()  # 确保没有读者
        print(f"✍️ 写者 {writer_id} 正在写入...")
        time.sleep(random.uniform(3, 6))  # 模拟写入时间

        # 释放资源
        print(f"✅ 写者 {writer_id} 完成写入，离开。")
        room_empty.release()


# 创建线程
reader_threads = []
writer_threads = []

# 创建 6 个读者线程
for i in range(6):
    t = threading.Thread(target=reader, args=(i,))
    reader_threads.append(t)
    t.start()

# 创建 2 个写者线程
for i in range(2):
    t = threading.Thread(target=writer, args=(i,))
    writer_threads.append(t)
    t.start()

# 等待所有线程执行（因为是无限循环，不会真正结束）
for t in reader_threads + writer_threads:
    t.join()
