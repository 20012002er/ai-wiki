#!/usr/bin/env python3
"""
测试脚本验证ref参数功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.crawl_gitlab_files import crawl_gitlab_files

def test_ref_parameter():
    """测试ref参数功能"""
    print("=== 测试ref参数功能 ===")
    
    # 测试用例1：使用用户指定的ref参数
    print("\n1. 测试使用用户指定的ref参数")
    try:
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test",
            token=None,
            ref="main",  # 用户明确指定ref
            debug=True,
            max_file_size=10000,
            include_patterns={"*.md"}
        )
        print(f"✅ 使用ref参数测试成功！获取到 {len(result.get('files', {}))} 个文件")
    except Exception as e:
        print(f"❌ 使用ref参数测试失败: {e}")
    
    # 测试用例2：不使用ref参数，让系统自动解析
    print("\n2. 测试不使用ref参数（自动解析）")
    try:
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test/-/tree/main",
            token=None,
            debug=True,
            max_file_size=10000,
            include_patterns={"*.md"}
        )
        print(f"✅ 自动解析ref测试成功！获取到 {len(result.get('files', {}))} 个文件")
    except Exception as e:
        print(f"❌ 自动解析ref测试失败: {e}")
    
    # 测试用例3：使用无效的ref参数
    print("\n3. 测试使用无效的ref参数")
    try:
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test",
            token=None,
            ref="invalid-branch-name",  # 无效的分支名
            debug=True,
            max_file_size=10000,
            include_patterns={"*.md"}
        )
        files_count = len(result.get('files', {}))
        if files_count == 0:
            print("✅ 无效ref参数测试成功（正确返回空文件列表）")
        else:
            print(f"⚠️  无效ref参数测试：获取到 {files_count} 个文件（可能分支存在）")
    except Exception as e:
        print(f"❌ 无效ref参数测试失败: {e}")

def test_api_integration():
    """测试API集成"""
    print("\n=== 测试API集成 ===")
    
    try:
        from nodes import FetchRepo
        
        # 模拟API请求
        shared = {
            "repo_url": "https://gitlab.com/gitlab-org/gitlab-test",
            "ref": "main",  # 用户指定的ref
            "include_patterns": {"*.md"},
            "exclude_patterns": set(),
            "max_file_size": 10000,
            "gitlab_token": None
        }
        
        node = FetchRepo()
        prep_res = node.prep(shared)
        
        # 检查ref参数是否正确传递
        if "ref" in prep_res and prep_res["ref"] == "main":
            print("✅ API集成测试成功 - ref参数正确传递")
        else:
            print("❌ API集成测试失败 - ref参数未正确传递")
            
    except Exception as e:
        print(f"❌ API集成测试失败: {e}")

if __name__ == "__main__":
    test_ref_parameter()
    test_api_integration()
    print("\n=== 测试完成 ===")