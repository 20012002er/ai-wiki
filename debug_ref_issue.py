#!/usr/bin/env python3
"""
调试脚本用于重现和分析GitLab ref参数问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.crawl_gitlab_files import crawl_gitlab_files
from urllib.parse import urlparse

def debug_ref_parsing():
    """调试ref参数解析逻辑"""
    print("=== 调试GitLab ref参数解析 ===")
    
    # 测试不同的URL格式
    test_urls = [
        "https://gitlab.com/gitlab-org/gitlab-test",
        "https://gitlab.com/gitlab-org/gitlab-test/-/tree/main",
        "https://gitlab.com/gitlab-org/gitlab-test/-/tree/master",
        "https://gitlab.com/gitlab-org/gitlab-test/-/tree/main/src",
        "https://gitlab.com/gitlab-org/gitlab-test/-/tree/invalid-branch",
    ]
    
    for url in test_urls:
        print(f"\n--- 测试URL: {url} ---")
        
        # 手动解析URL来理解逻辑
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        print(f"解析的路径部分: {path_parts}")
        
        # 模拟代码中的ref解析逻辑
        ref = None
        specific_path = ""
        
        if len(path_parts) > 3 and 'tree' == path_parts[3]:
            print(f"检测到tree路径，开始解析ref...")
            
            # 模拟join_parts函数
            join_parts = lambda i: '/'.join(path_parts[i:])
            relevant_path = join_parts(4)
            print(f"相关路径: {relevant_path}")
            
            # 这里应该调用fetch_branches，但我们先模拟
            print(f"假设获取分支列表成功，开始匹配ref...")
            
            # 模拟分支匹配逻辑
            branch_names = ["main", "master", "develop"]  # 假设的分支列表
            ref = next((name for name in branch_names if relevant_path.startswith(name)), None)
            
            print(f"匹配到的ref: {ref}")
            
            if ref:
                # 计算specific_path
                # Path format: namespace/project/-/tree/ref/path
                # So we start from index 5 (after ref)
                part_index = 5
                specific_path = join_parts(part_index) if part_index < len(path_parts) else ""
                print(f"计算出的specific_path: {specific_path}")
            else:
                print("未匹配到任何分支")
        else:
            print("URL不包含tree路径，使用默认分支")
            ref = None
            specific_path = ""
        
        print(f"最终结果 - ref: {ref}, specific_path: {specific_path}")

def test_actual_calls():
    """测试实际的API调用"""
    print("\n=== 测试实际API调用 ===")
    
    # 使用debug模式来查看详细的API调用信息
    try:
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test/-/tree/main",
            token=None,
            debug=True,
            max_file_size=10000,
            include_patterns={"*.md"}
        )
        print(f"API调用结果: {result is not None}")
    except Exception as e:
        print(f"API调用出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ref_parsing()
    test_actual_calls()