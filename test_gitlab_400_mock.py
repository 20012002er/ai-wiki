#!/usr/bin/env python3
"""
模拟测试GitLab 400错误处理逻辑
"""

import unittest
from unittest.mock import patch, MagicMock
from utils.crawl_gitlab_files import crawl_gitlab_files

class TestGitLab400Fix(unittest.TestCase):
    
    def test_400_error_handling(self):
        """测试400错误处理逻辑"""
        print("测试400错误处理逻辑...")
        
        # 模拟GitLab API返回400错误
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "Bad request", "message": "Invalid ref parameter"}'
        
        with patch('utils.crawl_gitlab_files.requests.get', return_value=mock_response):
            try:
                result = crawl_gitlab_files(
                    repo_url="https://gitlab.com/test/user/test-repo",
                    token="test-token",
                    debug=True
                )
                
                # 应该返回空结果而不是抛出异常
                self.assertIsNotNone(result)
                self.assertEqual(result["files"], {})
                print("✅ 400错误处理测试通过 - 正确处理了400错误")
                
            except Exception as e:
                self.fail(f"400错误处理失败: {e}")
    
    def test_branch_api_400_handling(self):
        """测试分支API的400错误处理"""
        print("测试分支API的400错误处理...")
        
        # 模拟分支API返回400错误
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "Project not found"}'
        
        with patch('utils.crawl_gitlab_files.requests.get', return_value=mock_response):
            try:
                result = crawl_gitlab_files(
                    repo_url="https://gitlab.com/invalid/user/repo/-/tree/main",
                    token="test-token",
                    debug=True
                )
                
                # 应该返回空结果而不是抛出异常
                self.assertIsNotNone(result)
                self.assertEqual(result["files"], {})
                print("✅ 分支API 400错误处理测试通过")
                
            except Exception as e:
                self.fail(f"分支API 400错误处理失败: {e}")
    
    def test_file_download_400_handling(self):
        """测试文件下载的400错误处理"""
        print("测试文件下载的400错误处理...")
        
        # 模拟tree API成功返回文件列表
        tree_response = MagicMock()
        tree_response.status_code = 200
        tree_response.json.return_value = [
            {"path": "test.py", "type": "blob"}
        ]
        
        # 模拟文件下载API返回400错误
        file_response = MagicMock()
        file_response.status_code = 400
        file_response.text = '{"error": "Invalid file path"}'
        
        with patch('utils.crawl_gitlab_files.requests.get') as mock_get:
            # 第一次调用返回tree数据，第二次调用返回400错误
            mock_get.side_effect = [tree_response, file_response]
            
            try:
                result = crawl_gitlab_files(
                    repo_url="https://gitlab.com/test/user/repo",
                    token="test-token",
                    debug=True,
                    include_patterns={"*.py"}
                )
                
                # 应该返回空文件列表但不会崩溃
                self.assertIsNotNone(result)
                self.assertEqual(result["files"], {})
                print("✅ 文件下载400错误处理测试通过")
                
            except Exception as e:
                self.fail(f"文件下载400错误处理失败: {e}")

if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)