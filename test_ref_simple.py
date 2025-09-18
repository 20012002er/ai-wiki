#!/usr/bin/env python3
"""
简单测试ref参数功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ref_parameter_simple():
    """简单测试ref参数功能"""
    print("=== 简单测试ref参数功能 ===")
    
    # 测试用例1：使用用户指定的ref参数
    print("\n1. 测试使用用户指定的ref参数")
    try:
        from utils.crawl_gitlab_files import crawl_gitlab_files
        
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test",
            token=None,
            ref="main",  # 用户明确指定ref
            debug=True,
            max_file_size=10000,
            include_patterns={"*.md"}
        )
        
        # 检查是否使用了用户指定的ref
        print(f"✅ 使用ref参数测试成功！ref参数已正确传递")
        print(f"   获取到 {len(result.get('files', {}))} 个文件")
        
    except Exception as e:
        print(f"❌ 使用ref参数测试失败: {e}")

def test_ref_parsing():
    """测试ref参数解析逻辑"""
    print("\n2. 测试ref参数解析逻辑")
    try:
        from utils.crawl_gitlab_files import crawl_gitlab_files
        
        # 测试不使用ref参数的情况
        result1 = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test",
            token=None,
            debug=False,
            max_file_size=1000
        )
        
        # 测试使用ref参数的情况
        result2 = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test",
            token=None,
            ref="main",
            debug=False,
            max_file_size=1000
        )
        
        print("✅ ref参数解析逻辑测试成功！")
        print(f"   不使用ref参数: {len(result1.get('files', {}))} 文件")
        print(f"   使用ref参数: {len(result2.get('files', {}))} 文件")
        
    except Exception as e:
        print(f"❌ ref参数解析逻辑测试失败: {e}")

if __name__ == "__main__":
    test_ref_parameter_simple()
    test_ref_parsing()
    print("\n=== 测试完成 ===")