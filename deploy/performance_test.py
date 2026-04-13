#!/usr/bin/env python3
import time
import requests
import threading
import json
from datetime import datetime

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_DURATION = 60  # 测试持续时间（秒）
CONCURRENT_REQUESTS = 10  # 并发请求数

# 测试结果
results = {
    "start_time": None,
    "end_time": None,
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "response_times": [],
    "errors": []
}

# 锁，用于线程安全地更新结果
lock = threading.Lock()

# 测试API响应时间
def test_api_response():
    """测试API响应时间"""
    endpoints = [
        "/",
        "/api/health",
        "/docs",
        "/redoc"
    ]
    
    print("测试API响应时间...")
    for endpoint in endpoints:
        url = f"{BASE_URL}{endpoint}"
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            with lock:
                results["total_requests"] += 1
                if response.status_code == 200:
                    results["successful_requests"] += 1
                    results["response_times"].append(response_time)
                    print(f"{endpoint}: {response_time:.2f}ms")
                else:
                    results["failed_requests"] += 1
                    results["errors"].append(f"{endpoint}: HTTP {response.status_code}")
                    print(f"{endpoint}: 失败 (HTTP {response.status_code})")
        except Exception as e:
            with lock:
                results["total_requests"] += 1
                results["failed_requests"] += 1
                results["errors"].append(f"{endpoint}: {str(e)}")
                print(f"{endpoint}: 失败 ({str(e)})")

# 并发测试函数
def concurrent_test():
    """并发测试"""
    def worker():
        """并发请求 worker"""
        url = f"{BASE_URL}/"
        while time.time() < results["end_time"]:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                with lock:
                    results["total_requests"] += 1
                    if response.status_code == 200:
                        results["successful_requests"] += 1
                        results["response_times"].append(response_time)
                    else:
                        results["failed_requests"] += 1
                        results["errors"].append(f"并发请求: HTTP {response.status_code}")
            except Exception as e:
                with lock:
                    results["total_requests"] += 1
                    results["failed_requests"] += 1
                    results["errors"].append(f"并发请求: {str(e)}")

    print(f"启动{CONCURRENT_REQUESTS}个并发请求...")
    threads = []
    for _ in range(CONCURRENT_REQUESTS):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        threads.append(t)
    
    # 等待测试结束
    for t in threads:
        t.join()

# 生成测试报告
def generate_report():
    """生成测试报告"""
    print("\n=== 性能测试报告 ===")
    print(f"测试时间: {results['start_time']} 到 {results['end_time']}")
    print(f"总请求数: {results['total_requests']}")
    print(f"成功请求数: {results['successful_requests']}")
    print(f"失败请求数: {results['failed_requests']}")
    
    if results['response_times']:
        avg_response_time = sum(results['response_times']) / len(results['response_times'])
        min_response_time = min(results['response_times'])
        max_response_time = max(results['response_times'])
        print(f"平均响应时间: {avg_response_time:.2f}ms")
        print(f"最小响应时间: {min_response_time:.2f}ms")
        print(f"最大响应时间: {max_response_time:.2f}ms")
    
    if results['errors']:
        print("\n错误信息:")
        for error in results['errors'][:10]:  # 只显示前10个错误
            print(f"- {error}")
        if len(results['errors']) > 10:
            print(f"... 还有 {len(results['errors']) - 10} 个错误")

# 主函数
def main():
    """主函数"""
    print("=== LanFileHub 性能测试 ===")
    print(f"测试目标: {BASE_URL}")
    print(f"测试持续时间: {TEST_DURATION}秒")
    print(f"并发请求数: {CONCURRENT_REQUESTS}")
    
    # 开始测试
    results["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results["end_time"] = time.time() + TEST_DURATION
    
    # 先测试API响应时间
    test_api_response()
    
    # 然后进行并发测试
    concurrent_test()
    
    # 结束测试
    results["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 生成报告
    generate_report()

if __name__ == "__main__":
    main()