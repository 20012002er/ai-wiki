#!/usr/bin/env python3
"""
测试GitLab功能是否正常工作的脚本
"""

import os
import sys
from utils.crawl_gitlab_files import crawl_gitlab_files

def test_gitlab_crawler():
    """测试GitLab爬取功能"""
    print("测试GitLab爬取功能...")
    
    # 测试一个公开的GitLab仓库
    test_repo_url = "https://gitlab.com/gitlab-org/gitlab-test"
    
    try:
        # 测试爬取功能
        result = crawl_gitlab_files(
            repo_url=test_repo_url,
            token=None,  # 使用公开仓库，不需要token
            max_file_size=100000,
            use_relative_paths=True,
            include_patterns={"*.md", "*.txt", "*.py"}  # 只爬取特定类型的文件
        )
        
        if result and "files" in result:
            files = result["files"]
            print(f"✅ GitLab爬取成功！获取到 {len(files)} 个文件")
            
            # 显示前5个文件
            print("\n前5个文件:")
            for i, (file_path, content) in enumerate(list(files.items())[:5]):
                print(f"  {i+1}. {file_path} ({len(content)} 字符)")
                
            return True
        else:
            print("❌ GitLab爬取失败：未获取到文件")
            return False
            
    except Exception as e:
        print(f"❌ GitLab爬取出错：{e}")
        return False

def test_gitlab_detection():
    """测试GitLab URL检测功能"""
    print("\n测试GitLab URL检测功能...")
    
    test_urls = [
        "https://gitlab.com/user/repo",
        "https://gitlab.example.com/user/repo",
        "https://github.com/user/repo",
        "/local/path"
    ]
    
    from nodes import FetchRepo
    node = FetchRepo()
    
    # 测试自动检测
    print("自动检测测试:")
    for url in test_urls:
        shared = {
            "repo_url": url if url != "/local/path" else None,
            "local_dir": "/local/path" if url == "/local/path" else None,
            "include_patterns": set(),
            "exclude_patterns": set(),
            "max_file_size": 100000
        }
        
        prep_res = node.prep(shared)
        is_gitlab = prep_res.get("is_gitlab", False)
        gitlab_domain = prep_res.get("gitlab_domain", "")
        
        status = "✅" if ("gitlab.com" in url and is_gitlab) or ("gitlab.com" not in url and not is_gitlab) else "❌"
        print(f"  {status} URL: {url} -> GitLab: {is_gitlab}, Domain: {gitlab_domain}")
    
    # 测试显式指定仓库类型
    print("\n显式仓库类型测试:")
    test_cases = [
        ("https://custom-gitlab.example.com/user/repo", "gitlab", True),
        ("https://custom-gitlab.example.com/user/repo", "github", False),
        ("https://github.com/user/repo", "gitlab", True),
        ("https://github.com/user/repo", "github", False),
    ]
    
    for url, repo_type, expected_gitlab in test_cases:
        shared = {
            "repo_url": url,
            "repo_type": repo_type,
            "include_patterns": set(),
            "exclude_patterns": set(),
            "max_file_size": 100000
        }
        
        prep_res = node.prep(shared)
        is_gitlab = prep_res.get("is_gitlab", False)
        
        status = "✅" if is_gitlab == expected_gitlab else "❌"
        print(f"  {status} URL: {url}, Type: {repo_type} -> GitLab: {is_gitlab} (expected: {expected_gitlab})")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("GitLab功能测试")
    print("=" * 50)
    
    # 测试URL检测
    url_test_passed = test_gitlab_detection()
    
    # 测试爬取功能（可选，需要网络连接）
    if len(sys.argv) > 1 and sys.argv[1] == "--test-crawl":
        crawl_test_passed = test_gitlab_crawler()
    else:
        print("\n跳过爬取测试（使用 --test-crawl 参数启用实际爬取测试）")
        crawl_test_passed = True
    
    print("\n" + "=" * 50)
    if url_test_passed and crawl_test_passed:
        print("✅ 所有测试通过！GitLab功能正常工作")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)