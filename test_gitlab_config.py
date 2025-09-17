#!/usr/bin/env python3
"""
测试 GitLab 配置功能
"""

import os
import sys
sys.path.append('.')

from utils.crawl_gitlab_files import crawl_gitlab_files

def test_config_loading():
    """测试配置加载功能"""
    print("测试 GitLab 配置加载...")
    
    # 测试默认配置
    print("\n1. 测试默认配置:")
    result = crawl_gitlab_files(
        "https://gitlab.com/gitlab-org/gitlab/-/tree/master/doc",
        max_file_size=1024,  # 限制文件大小以快速测试
        include_patterns={"*.md"}  # 只获取 markdown 文件
    )
    
    if result and 'stats' in result:
        stats = result['stats']
        print(f"  域名: {stats.get('gitlab_domain', 'N/A')}")
        print(f"  协议: {stats.get('gitlab_protocol', 'N/A')}")
    
    # 测试环境变量配置
    print("\n2. 测试环境变量配置:")
    os.environ['GITLAB_DOMAIN'] = 'gitlab.example.com'
    os.environ['GITLAB_PROTOCOL'] = 'http'
    
    result = crawl_gitlab_files(
        "https://gitlab.example.com/user/project/-/tree/main",
        max_file_size=1024
    )
    
    if result and 'stats' in result:
        stats = result['stats']
        print(f"  域名: {stats.get('gitlab_domain', 'N/A')}")
        print(f"  协议: {stats.get('gitlab_protocol', 'N/A')}")
    
    # 清理环境变量
    if 'GITLAB_DOMAIN' in os.environ:
        del os.environ['GITLAB_DOMAIN']
    if 'GITLAB_PROTOCOL' in os.environ:
        del os.environ['GITLAB_PROTOCOL']
    
    # 测试参数覆盖
    print("\n3. 测试参数覆盖:")
    result = crawl_gitlab_files(
        "https://custom.gitlab.com/user/project/-/tree/main",
        gitlab_domain="custom.gitlab.com",
        gitlab_protocol="https",
        max_file_size=1024
    )
    
    if result and 'stats' in result:
        stats = result['stats']
        print(f"  域名: {stats.get('gitlab_domain', 'N/A')}")
        print(f"  协议: {stats.get('gitlab_protocol', 'N/A')}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_config_loading()