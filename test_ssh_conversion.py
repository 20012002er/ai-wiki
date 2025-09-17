#!/usr/bin/env python3
"""
测试GitLab SSH URL转换功能
"""

import sys
sys.path.append('.')

from utils.crawl_gitlab_files import crawl_gitlab_files

def test_ssh_url_conversion():
    """测试SSH URL到HTTP URL的转换功能"""
    print("测试GitLab SSH URL转换功能...")
    
    # 测试用例
    test_cases = [
        {
            "name": "SSH URL with git@ format",
            "url": "git@gitlab.example.com:user/project.git",
            "expected_domain": "gitlab.example.com",
            "expected_path": "user/project"
        },
        {
            "name": "SSH URL without .git suffix",
            "url": "git@gitlab.example.com:user/project",
            "expected_domain": "gitlab.example.com", 
            "expected_path": "user/project"
        },
        {
            "name": "HTTP URL (should not be converted)",
            "url": "https://gitlab.example.com/user/project",
            "expected_domain": "gitlab.example.com",
            "expected_path": "user/project"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"输入URL: {test_case['url']}")
        
        try:
            # 测试URL转换逻辑
            result = crawl_gitlab_files(
                repo_url=test_case['url'],
                token="test_token",
                gitlab_domain="gitlab.example.com",
                gitlab_protocol="https",
                max_file_size=1024
            )
            
            if result and 'stats' in result:
                print(f"✅ 转换成功")
                print(f"   使用的域名: {result['stats'].get('gitlab_domain', 'N/A')}")
                print(f"   使用的协议: {result['stats'].get('gitlab_protocol', 'N/A')}")
            else:
                print(f"❌ 转换失败或API调用失败")
                
        except Exception as e:
            print(f"❌ 发生错误: {e}")
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_ssh_url_conversion()