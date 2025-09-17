#!/usr/bin/env python3
"""
测试自定义GitLab域名功能
"""

import os
import sys
sys.path.append('.')

from nodes import FetchRepo

def test_custom_gitlab_domain():
    """测试自定义GitLab域名功能"""
    print("测试自定义GitLab域名功能...")
    
    # 测试场景1: 自定义域名 + 显式指定repo-type
    print("\n1. 测试自定义域名 + 显式指定repo-type:")
    shared = {
        "repo_url": "https://custom-gitlab.example.com/user/project/-/tree/main",
        "repo_type": "gitlab",
        "gitlab_token": "test_token",
        "include_patterns": set(),
        "exclude_patterns": set(),
        "max_file_size": 100000
    }
    
    node = FetchRepo()
    prep_res = node.prep(shared)
    
    print(f"  URL: {prep_res['repo_url']}")
    print(f"  Is GitLab: {prep_res['is_gitlab']}")
    print(f"  GitLab Domain: {prep_res['gitlab_domain']}")
    
    # 验证结果
    assert prep_res['is_gitlab'] == True, "应该识别为GitLab仓库"
    assert prep_res['gitlab_domain'] == "custom-gitlab.example.com", f"域名应该是 custom-gitlab.example.com，但得到的是 {prep_res['gitlab_domain']}"
    
    # 测试场景2: 自定义域名 + 自动检测（现在应该能正确识别）
    print("\n2. 测试自定义域名 + 自动检测:")
    shared2 = {
        "repo_url": "https://custom-gitlab.example.com/user/project/-/tree/main",
        "include_patterns": set(),
        "exclude_patterns": set(),
        "max_file_size": 100000
    }
    
    prep_res2 = node.prep(shared2)
    print(f"  URL: {prep_res2['repo_url']}")
    print(f"  Is GitLab: {prep_res2['is_gitlab']}")
    print(f"  GitLab Domain: {prep_res2['gitlab_domain']}")
    
    # 现在自动检测应该能正确识别自定义GitLab域名
    assert prep_res2['is_gitlab'] == True, "自动检测应该识别为GitLab仓库"
    assert prep_res2['gitlab_domain'] == "custom-gitlab.example.com", f"域名应该是 custom-gitlab.example.com，但得到的是 {prep_res2['gitlab_domain']}"
    
    # 测试场景3: 标准GitLab域名 + 自动检测
    print("\n3. 测试标准GitLab域名 + 自动检测:")
    shared3 = {
        "repo_url": "https://gitlab.com/user/project/-/tree/main",
        "include_patterns": set(),
        "exclude_patterns": set(),
        "max_file_size": 100000
    }
    
    prep_res3 = node.prep(shared3)
    print(f"  URL: {prep_res3['repo_url']}")
    print(f"  Is GitLab: {prep_res3['is_gitlab']}")
    print(f"  GitLab Domain: {prep_res3['gitlab_domain']}")
    
    assert prep_res3['is_gitlab'] == True, "应该识别为GitLab仓库"
    assert prep_res3['gitlab_domain'] == "gitlab.com", f"域名应该是 gitlab.com，但得到的是 {prep_res3['gitlab_domain']}"
    
    print("\n✅ 所有测试通过！自定义GitLab域名功能修复成功。")

if __name__ == "__main__":
    test_custom_gitlab_domain()