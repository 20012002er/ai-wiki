#!/usr/bin/env python3
"""
测试GitLab SSH URL转换逻辑（不进行实际API调用）
"""

import sys
sys.path.append('.')

from urllib.parse import urlparse

def test_ssh_url_conversion_logic():
    """测试SSH URL到HTTP URL的转换逻辑"""
    print("测试GitLab SSH URL转换逻辑...")
    
    def convert_ssh_to_http(repo_url, gitlab_protocol="https", gitlab_domain="gitlab.com"):
        """模拟URL转换逻辑"""
        # Detect SSH URL (git@ or .git suffix)
        is_ssh_url = repo_url.startswith("git@") or repo_url.endswith(".git")
        
        if is_ssh_url:
            print(f"Converting SSH URL to HTTP format: {repo_url}")
            
            if repo_url.startswith("git@"):
                # Convert git@gitlab.example.com:user/project.git to https://gitlab.example.com/user/project
                ssh_parts = repo_url.split("@")[1].split(":")
                if len(ssh_parts) == 2:
                    domain = ssh_parts[0]
                    path = ssh_parts[1].replace(".git", "")
                    repo_url = f"{gitlab_protocol}://{domain}/{path}"
                    print(f"Converted SSH URL to: {repo_url}")
                else:
                    print(f"Warning: Unable to parse SSH URL: {repo_url}")
            elif repo_url.endswith(".git"):
                # Remove .git suffix for cleaner API usage
                repo_url = repo_url[:-4]
                print(f"Removed .git suffix: {repo_url}")
            
            print("Using API access instead of SSH cloning for better authentication support")
        
        return repo_url
    
    # 测试用例
    test_cases = [
        {
            "name": "SSH URL with git@ format",
            "url": "git@gitlab.example.com:user/project.git",
            "expected": "https://gitlab.example.com/user/project"
        },
        {
            "name": "SSH URL without .git suffix", 
            "url": "git@gitlab.example.com:user/project",
            "expected": "https://gitlab.example.com/user/project"
        },
        {
            "name": "HTTP URL (should not be converted)",
            "url": "https://gitlab.example.com/user/project",
            "expected": "https://gitlab.example.com/user/project"
        },
        {
            "name": "Custom domain SSH URL",
            "url": "git@custom.gitlab.com:namespace/project.git",
            "expected": "https://custom.gitlab.com/namespace/project"
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"输入URL: {test_case['url']}")
        
        converted_url = convert_ssh_to_http(test_case['url'], "https", "gitlab.example.com")
        
        if converted_url == test_case['expected']:
            print(f"✅ 转换成功: {converted_url}")
        else:
            print(f"❌ 转换失败")
            print(f"   期望: {test_case['expected']}")
            print(f"   实际: {converted_url}")
            all_passed = False
    
    print(f"\n{'✅ 所有测试通过！' if all_passed else '❌ 部分测试失败'}")
    return all_passed

if __name__ == "__main__":
    test_ssh_url_conversion_logic()