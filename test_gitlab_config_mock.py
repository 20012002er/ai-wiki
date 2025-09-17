#!/usr/bin/env python3
"""
测试 GitLab 配置功能（模拟测试）
"""

import os
import sys
sys.path.append('.')

from unittest.mock import patch, MagicMock
from utils.crawl_gitlab_files import crawl_gitlab_files

def test_config_loading_mock():
    """测试配置加载功能（使用模拟）"""
    print("测试 GitLab 配置加载（模拟测试）...")
    
    # 模拟 requests.get 返回空结果
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = []
    
    with patch('utils.crawl_gitlab_files.requests.get', return_value=mock_response):
        # 测试默认配置
        print("\n1. 测试默认配置:")
        result = crawl_gitlab_files(
            "https://gitlab.com/gitlab-org/gitlab/-/tree/master/doc",
            max_file_size=1024,
            include_patterns={"*.md"}
        )
        
        if result and 'stats' in result:
            stats = result['stats']
            print(f"  域名: {stats.get('gitlab_domain', 'N/A')}")
            print(f"  协议: {stats.get('gitlab_protocol', 'N/A')}")
            assert stats.get('gitlab_domain') == "gitlab.com", "默认域名应该是 gitlab.com"
            assert stats.get('gitlab_protocol') == "https", "默认协议应该是 https"
        
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
            assert stats.get('gitlab_domain') == "gitlab.example.com", "环境变量域名应该是 gitlab.example.com"
            assert stats.get('gitlab_protocol') == "http", "环境变量协议应该是 http"
        
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
            assert stats.get('gitlab_domain') == "custom.gitlab.com", "参数域名应该是 custom.gitlab.com"
            assert stats.get('gitlab_protocol') == "https", "参数协议应该是 https"
    
    print("\n✅ 所有模拟测试通过！GitLab配置功能正常。")

if __name__ == "__main__":
    test_config_loading_mock()