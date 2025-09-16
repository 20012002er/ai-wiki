#!/usr/bin/env python3
"""
启动脚本用于运行Tutorial Generation API服务器
"""

import os
import sys
import uvicorn
from api_server import app

def main():
    """主函数，启动API服务器"""
    # 设置默认主机和端口
    host = os.environ.get('API_HOST', '0.0.0.0')
    port = int(os.environ.get('API_PORT', '8000'))
    
    print(f"🚀 Starting Tutorial Generation API Server")
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"❤️  Health Check: http://{host}:{port}/health")
    print("-" * 50)
    
    # 启动服务器
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False  # 生产环境建议关闭热重载
    )

if __name__ == "__main__":
    main()