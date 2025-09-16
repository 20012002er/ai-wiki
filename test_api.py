#!/usr/bin/env python3
"""
API功能测试脚本
用于验证Tutorial Generation API的基本功能
"""

import requests
import json
import time
import sys

def test_health_check():
    """测试健康检查端点"""
    print("🧪 Testing health check endpoint...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Health check passed")
                return True
            else:
                print("❌ Health check failed - invalid response")
                return False
        else:
            print(f"❌ Health check failed - status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed - cannot connect to server")
        print("   Make sure the API server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Health check failed - unexpected error: {e}")
        return False

def test_generate_tutorial():
    """测试教程生成端点"""
    print("\n🧪 Testing tutorial generation endpoint...")
    
    # 测试数据 - 使用一个小的本地目录或公开的GitHub仓库
    test_data = {
        "repo_url": "https://github.com/yankils/hello-world",  # GitHub示例仓库
        "project_name": "hello-world-test",
        "language": "english",
        "output_dir": "test_output",
        "max_file_size": 50000,
        "use_cache": True,
        "max_abstractions": 3
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/generate-tutorial",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job_id")
            print(f"✅ Tutorial generation started - Job ID: {job_id}")
            return job_id
        else:
            print(f"❌ Tutorial generation failed - status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Tutorial generation failed - error: {e}")
        return None

def test_job_status(job_id):
    """测试任务状态查询"""
    print(f"\n🧪 Testing job status for ID: {job_id}")
    
    try:
        response = requests.get(
            f"http://localhost:8000/job/{job_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status")
            print(f"✅ Job status: {status}")
            return status
        else:
            print(f"❌ Job status check failed - status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Job status check failed - error: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 Starting API functionality tests")
    print("=" * 50)
    
    # 测试健康检查
    if not test_health_check():
        print("\n❌ API server is not ready. Please start the server first.")
        print("   Run: python run_api.py")
        sys.exit(1)
    
    # 测试教程生成
    job_id = test_generate_tutorial()
    if not job_id:
        print("\n❌ Tutorial generation test failed")
        sys.exit(1)
    
    # 等待一段时间后检查任务状态
    print(f"\n⏳ Waiting 10 seconds for job processing...")
    time.sleep(10)
    
    # 检查任务状态
    status = test_job_status(job_id)
    if status:
        if status in ["completed", "running"]:
            print(f"\n✅ API functionality test completed successfully!")
            print(f"   Job ID: {job_id}")
            print(f"   Status: {status}")
            print(f"\n📋 Next steps:")
            print(f"   1. Check job status: GET /job/{job_id}")
            print(f"   2. Download results: GET /download/{job_id}")
            print(f"   3. View API docs: http://localhost:8000/docs")
        else:
            print(f"\n⚠️  Job status: {status} - check server logs for details")
    else:
        print("\n❌ Job status check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()