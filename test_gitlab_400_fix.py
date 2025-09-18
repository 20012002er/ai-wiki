#!/usr/bin/env python3
"""
测试脚本用于验证GitLab 400错误修复
"""

import os
import sys
from utils.crawl_gitlab_files import crawl_gitlab_files

def test_gitlab_400_fix():
    """测试GitLab 400错误修复"""
    print("测试GitLab 400错误修复...")
    
    # 测试用例1：使用公开仓库测试基本功能
    print("\n1. 测试公开仓库基本功能:")
    try:
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test",
            token=None,
            debug=True,
            max_file_size=100000,
            include_patterns={"*.md", "*.txt"}
        )
        
        if result and "files" in result:
            print(f"✅ 公开仓库测试成功！获取到 {len(result['files'])} 个文件")
        else:
            print("❌ 公开仓库测试失败")
            
    except Exception as e:
        print(f"❌ 公开仓库测试出错: {e}")
    
    # 测试用例2：测试错误处理（使用无效的ref参数）
    print("\n2. 测试400错误处理:")
    try:
        # 这个测试会触发400错误，因为ref参数无效
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test/-/tree/invalid-branch-name",
            token=None,
            debug=True,
            max_file_size=100000
        )
        
        print("✅ 400错误处理测试完成（应该显示详细的错误信息）")
        
    except Exception as e:
        print(f"❌ 400错误处理测试出错: {e}")
    
    # 测试用例3：测试URL编码
    print("\n3. 测试URL编码改进:")
    try:
        result = crawl_gitlab_files(
            repo_url="https://gitlab.com/gitlab-org/gitlab-test/-/tree/master/README.md",
            token=None,
            debug=True,
            max_file_size=100000
        )
        
        if result and "files" in result:
            print(f"✅ URL编码测试成功！获取到 {len(result['files'])} 个文件")
        else:
            print("❌ URL编码测试失败")
            
    except Exception as e:
        print(f"❌ URL编码测试出错: {e}")

if __name__ == "__main__":
    test_gitlab_400_fix()
    print("\n测试完成！")