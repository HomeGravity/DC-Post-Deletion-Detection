import psutil
import numpy as np

# CPU 사용량 모니터링
def monitor_cpu(interval):
    cpu_percent = psutil.cpu_percent(interval=interval)

    return np.round(cpu_percent, 1)

# 메모리 사용량 모니터링
def monitor_memory():
    memory = psutil.virtual_memory()
    used_memory = memory.used / (1024 * 1024) # 메모리 사용량을 MB 단위로 변환
    available_memory = memory.available / (1024 * 1024) # 사용 가능한 메모리 양을 MB 단위로 변환
    total_memory_percent = memory.percent # 사용 가능한 메모리 양을 퍼센트로 표시

    return np.round(used_memory, 1), np.round(available_memory, 1), np.round(total_memory_percent, 1)


# 네트워크 사용량 모니터링
def monitor_network():
    network = psutil.net_io_counters()
    sent_bytes = network.bytes_sent / (1024 * 1024) # 송신 데이터 양을 MB 단위로 변환
    recv_bytes = network.bytes_recv / (1024 * 1024) # 수신 데이터 양을 MB 단위로 변환

    return np.round(sent_bytes, 1), np.round(recv_bytes, 1) 



# CPU, RAM, 네트워크 사용량 표시
def UsagePerformance(interval = None):

    cpu_percent = monitor_cpu(interval)
    available_memory, used_memory, total_memory_percent = monitor_memory()
    sent_bytes, recv_bytes = monitor_network()

    print("CPU 사용량: %s%%" % cpu_percent)
    print("Memory 사용량: %sMB (%s%%)| 사용 가능한 Memory: %sMB" % (available_memory, total_memory_percent, used_memory))
    print("Network(송신): %sMB | Network(수신): %sMB" % (sent_bytes, recv_bytes))
    print()

    return cpu_percent, (available_memory, used_memory, total_memory_percent), (sent_bytes, recv_bytes)



# CPU, RAM, 네트워크 사용량 표시를 내 프로그램 형식에 맞게 변환
def UsagePerformanceTEXT(interval=None):
    cpu_percent, (available_memory, used_memory, total_memory_percent), (sent_bytes, recv_bytes) = UsagePerformance(interval)
    PerformanceTEXT = ""

    PerformanceTEXT += "\nCPU 사용량: %s%%\n" % cpu_percent
    PerformanceTEXT += "Memory 사용량: %sMB (%s%%)| 사용 가능한 Memory: %sMB\n" % (0, total_memory_percent, 0)
    PerformanceTEXT += "Network(송신): %sMB | Network(수신): %sMB\n\n" % (sent_bytes, recv_bytes)
    
    return PerformanceTEXT



# 사용 예시
if __name__ == "__main__":
    while True:
        UsagePerformanceTEXT(interval=None)
