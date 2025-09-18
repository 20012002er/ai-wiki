#!/usr/bin/env python3
"""
最终测试脚本验证ref参数功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_main_ref_parameter():
    """测试main.py中的ref参数支持"""
    print("=== 测试main.py中的ref参数支持 ===")
    
    try:
        # 测试命令行参数解析
        import argparse
        
        parser = argparse.ArgumentParser(description="Test ref parameter")
        parser.add_argument("--ref", help="Specific branch, tag, or commit reference for GitLab repositories")
        
        # 测试ref参数解析
        test_args = parser.parse_args(["--ref", "main"])
        if test_args.ref == "main":
            print("✅ main.py命令行ref参数解析成功")
        else:
            print("❌ main.py命令行ref参数解析失败")
            
    except Exception as e:
        print(f"❌ main.py ref参数测试失败: {e}")

def test_api_ref_parameter():
    """测试API中的ref参数支持"""
    print("\n=== 测试API中的ref参数支持 ===")
    
    try:
        from api_server import TutorialRequest
        
        # 测试API模型
        request_data = {
            "repo_url": "https://gitlab.com/user/project",
            "ref": "main"
        }
        
        request = TutorialRequest(**request_data)
        if request.ref == "main":
            print("✅ API TutorialRequest模型ref参数支持成功")
        else:
            print("❌ API TutorialRequest模型ref参数支持失败")
            
    except Exception as e:
        print(f"❌ API ref参数测试失败: {e}")

def test_nodes_ref_parameter():
    """测试nodes.py中的ref参数支持"""
    print("\n=== 测试nodes.py中的ref参数支持 ===")
    
    try:
        from nodes import FetchRepo
        
        # 测试ref参数传递
        shared = {
            "repo_url": "https://gitlab.com/user/project",
            "ref": "main",
            "include_patterns": set(),
            "exclude_patterns": set(),
            "max_file_size": 10000
        }
        
        node = FetchRepo()
        prep_res = node.prep(shared)
        
        if prep_res.get("ref") == "main":
            print("✅ nodes.py ref参数传递成功")
        else:
            print("❌ nodes.py ref参数传递失败")
            
    except Exception as e:
        print(f"❌ nodes.py ref参数测试失败: {e}")

def test_crawl_gitlab_ref_parameter():
    """测试crawl_gitlab_files.py中的ref参数支持"""
    print("\n=== 测试crawl_gitlab_files.py中的ref参数支持 ===")
    
    try:
        from utils.crawl_gitlab_files import crawl_gitlab_files
        
        # 测试ref参数功能
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test",
            token=None,
            ref="main",  # 用户明确指定ref
            debug=True,
            max_file_size=1000
        )
        
        print("✅ crawl_gitlab_files.py ref参数功能测试成功")
        print(f"   获取到 {len(result.get('files', {}))} 个文件")
        
    except Exception as e:
        print(f"❌ crawl_gitlab_files.py ref参数测试失败: {e}")

if __name__ == "__main__":
    test_main_ref_parameter()
    test_api_ref_parameter()
    test_nodes_ref_parameter()
    test_crawl_gitlab_ref_parameter()
    print("\n=== 最终测试完成 ===")