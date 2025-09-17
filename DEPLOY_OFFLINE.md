# 内网离线环境部署指南

本文档说明如何在内网离线环境中部署 Tutorial Generation API 项目，解决外部CDN依赖问题。

## 🎯 优化内容

已完成的优化包括：

1. **禁用外部CDN依赖** - 修改FastAPI配置，禁用默认的Swagger UI和ReDoc外部资源加载
2. **本地静态资源** - 创建本地静态文件目录，包含所有必要的Swagger UI资源
3. **自定义文档端点** - 实现完全离线的API文档页面
4. **静态文件服务** - 添加静态文件挂载，支持本地资源访问

## 📁 文件结构变化

```
项目根目录/
├── static/
│   └── docs/
│       ├── index.html          # 自定义Swagger UI页面
│       ├── swagger-ui.css      # Swagger UI样式文件
│       ├── swagger-ui-bundle.js      # Swagger UI主脚本
│       └── swagger-ui-standalone-preset.js  # Swagger UI独立预设
├── api_server.py               # 已优化的API服务器
├── download_swagger_assets.py  # Swagger资源下载脚本（可选）
├── check_offline_config.py     # 离线配置检查脚本
└── DEPLOY_OFFLINE.md          # 本部署指南
```

## 🚀 部署步骤

### 1. 准备环境

确保Python环境已安装所需依赖：

```bash
pip install -r requirements.txt
```

### 2. 验证配置

运行配置检查脚本确认离线环境准备就绪：

```bash
python check_offline_config.py
```

### 3. 启动服务

在内网环境中启动API服务器：

```bash
python run_api.py
```

或者直接运行：

```bash
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### 4. 访问文档

在浏览器中访问以下URL：

- **Swagger UI文档**: http://<服务器IP>:8000/docs
- **简化版文档**: http://<服务器IP>:8000/redoc  
- **健康检查**: http://<服务器IP>:8000/health
- **OpenAPI规范**: http://<服务器IP>:8000/openapi.json

## 🔧 自定义配置

### 修改主机和端口

可以通过环境变量修改服务器配置：

```bash
export API_HOST=0.0.0.0
export API_PORT=8000
python run_api.py
```

### 更新静态资源

如果需要更新Swagger UI资源：

1. 在有网络的环境中运行：
```bash
python download_swagger_assets.py
```

2. 将生成的 `static/docs/` 目录复制到内网环境

## 🌐 网络要求

优化后的部署完全不需要外部网络连接：

- ✅ 无需访问 `cdn.jsdelivr.net`
- ✅ 无需访问任何外部CDN
- ✅ 所有资源本地加载
- ✅ 支持完全离线的内网环境

## 🧪 测试验证

使用测试脚本验证离线功能：

```bash
python test_offline_docs.py
```

或者手动测试：

```bash
# 检查静态文件访问
curl http://localhost:8000/static/docs/swagger-ui.css

# 检查API文档访问
curl http://localhost:8000/docs
```

## 📝 注意事项

1. **首次部署**：确保 `static/docs/` 目录中的所有文件都存在
2. **防火墙设置**：内网环境中确保端口8000可访问
3. **资源更新**：如需更新Swagger UI版本，需要重新下载资源文件
4. **浏览器缓存**：首次访问后清除浏览器缓存以确保加载最新资源

## 🆘 故障排除

### 问题：文档页面无法加载
**解决方案**：检查静态文件目录权限和路径配置

### 问题：样式或脚本加载失败  
**解决方案**：运行 `python check_offline_config.py` 检查文件完整性

### 问题：端口被占用
**解决方案**：修改 `API_PORT` 环境变量使用其他端口

## 📞 支持

如有部署问题，请检查：
1. 静态文件目录是否存在且可读
2. API服务器配置是否正确
3. 网络防火墙设置

所有优化代码已集成到主代码库，无需额外配置即可支持内网离线部署。