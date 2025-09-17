#!/usr/bin/env python3
"""
检查离线环境配置
"""
import os
import sys

def check_static_files():
    """检查静态文件是否存在"""
    print("🔍 检查静态文件配置...")
    print("-" * 50)
    
    required_files = [
        "static/docs/index.html",
        "static/docs/swagger-ui.css", 
        "static/docs/swagger-ui-bundle.js",
        "static/docs/swagger-ui-standalone-preset.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - 存在")
        else:
            print(f"❌ {file_path} - 缺失")
            missing_files.append(file_path)
    
    return missing_files

def check_api_server_config():
    """检查API服务器配置"""
    print("\n🔍 检查API服务器配置...")
    print("-" * 50)
    
    try:
        with open("api_server.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("FastAPI配置禁用外部CDN", "docs_url=None" in content and "redoc_url=None" in content),
            ("静态文件挂载", "app.mount" in content and "StaticFiles" in content),
            ("自定义docs端点", "@app.get(\"/docs\"" in content),
            ("自定义redoc端点", "@app.get(\"/redoc\"" in content)
        ]
        
        all_passed = True
        for check_name, condition in checks:
            if condition:
                print(f"✅ {check_name} - 配置正确")
            else:
                print(f"❌ {check_name} - 配置缺失")
                all_passed = False
        
        return all_passed
        
    except FileNotFoundError:
        print("❌ api_server.py 文件不存在")
        return False

def main():
    print("🚀 离线环境配置检查")
    print("=" * 50)
    
    # 检查静态文件
    missing_files = check_static_files()
    
    # 检查服务器配置
    config_ok = check_api_server_config()
    
    print("\n" + "=" * 50)
    print("📊 检查结果汇总:")
    
    if not missing_files and config_ok:
        print("🎉 所有配置检查通过！")
        print("\n📝 部署说明:")
        print("1. 在内网环境中运行: python run_api.py")
        print("2. 访问 http://<服务器IP>:8000/docs 查看API文档")
        print("3. 所有资源均为本地加载，无需外部网络连接")
        return True
    else:
        if missing_files:
            print(f"⚠️  缺失文件: {len(missing_files)} 个")
            for file in missing_files:
                print(f"   - {file}")
        
        if not config_ok:
            print("⚠️  API服务器配置需要修复")
        
        print("\n❌ 请修复上述问题后重新检查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)