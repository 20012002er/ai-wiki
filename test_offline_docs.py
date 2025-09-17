#!/usr/bin/env python3
"""
测试离线环境下的docs端点访问
"""
import requests
import time
import subprocess
import sys

def test_offline_docs():
    """测试离线环境下的API文档访问"""
    
    # 启动API服务器
    print("🚀 启动API服务器...")
    server_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "api_server:app", 
        "--host", "0.0.0.0", "--port", "8000", "--reload", "False"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # 等待服务器启动
    time.sleep(3)
    
    test_urls = [
        "http://localhost:8000/docs",
        "http://localhost:8000/redoc", 
        "http://localhost:8000/health",
        "http://localhost:8000/openapi.json",
        "http://localhost:8000/static/docs/swagger-ui.css"
    ]
    
    print("\n🔍 测试离线环境访问:")
    print("-" * 50)
    
    success_count = 0
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - 成功 (状态码: {response.status_code})")
                success_count += 1
            else:
                print(f"❌ {url} - 失败 (状态码: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"❌ {url} - 错误: {e}")
    
    print("-" * 50)
    print(f"测试结果: {success_count}/{len(test_urls)} 个端点访问成功")
    
    # 停止服务器
    server_process.terminate()
    server_process.wait()
    
    if success_count == len(test_urls):
        print("🎉 所有测试通过！离线环境部署成功！")
        return True
    else:
        print("⚠️  部分测试失败，请检查配置")
        return False

if __name__ == "__main__":
    test_offline_docs()