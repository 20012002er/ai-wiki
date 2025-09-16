# Tutorial Generation API

将原有的命令行教程生成工具转换为RESTful API服务。

## 功能特性

- 🚀 RESTful API 接口
- 📚 支持GitHub仓库、GitLab仓库和本地目录分析
- 🌍 多语言教程生成
- ⚡ 异步任务处理
- 📦 结果文件下载
- 🔍 实时任务状态查询

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动API服务器

### 方式一：使用启动脚本
```bash
python run_api.py
```

### 方式二：直接运行
```bash
python api_server.py
```

### 方式三：使用环境变量配置
```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export OLLAMA_HOST=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen3:8b
python run_api.py
```

### 方式四：使用.env文件配置
创建 `.env` 文件：
```bash
cp .env.example .env
# 编辑 .env 文件配置您的设置
```

然后运行：
```bash
python run_api.py
```

## API端点

### 1. 生成教程
**POST** `/generate-tutorial`

请求体示例（GitHub）：
```json
{
  "repo_url": "https://github.com/username/repo",
  "project_name": "my-project",
  "github_token": "your_github_token",
  "language": "chinese",
  "output_dir": "output",
  "max_file_size": 100000,
  "use_cache": true,
  "max_abstractions": 10
}
```

请求体示例（GitLab）：
```json
{
  "repo_url": "https://gitlab.com/username/project",
  "project_name": "my-project",
  "gitlab_token": "your_gitlab_token",
  "language": "chinese",
  "output_dir": "output",
  "max_file_size": 100000,
  "use_cache": true,
  "max_abstractions": 10
}
```

或使用本地目录：
```json
{
  "local_dir": "/path/to/local/project",
  "project_name": "local-project",
  "language": "english"
}
```

请求体示例（显式指定仓库类型）：
```json
{
  "repo_url": "https://custom-gitlab.example.com/user/repo",
  "repo_type": "gitlab",
  "gitlab_token": "your_gitlab_token",
  "project_name": "my-project",
  "language": "chinese"
}
```

响应示例：
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "message": "Tutorial generation job started",
  "output_dir": "output"
}
```

### 2. 查询任务状态
**GET** `/job/{job_id}`

响应示例：
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "progress": {
    "step": "completed",
    "details": "completed"
  },
  "result": {
    "output_dir": "output/my-project",
    "files_generated": 15,
    "abstractions_identified": 8
  }
}
```

### 3. 下载生成结果
**GET** `/download/{job_id}`

返回生成的教程文件的ZIP压缩包。

### 4. 健康检查
**GET** `/health`

响应示例：
```json
{
  "status": "healthy",
  "service": "tutorial-generation-api"
}
```

## 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| repo_url | string | 否 | - | GitHub或GitLab仓库URL |
| local_dir | string | 否 | - | 本地目录路径 |
| project_name | string | 否 | - | 项目名称 |
| github_token | string | 否 | - | GitHub访问令牌 |
| gitlab_token | string | 否 | - | GitLab访问令牌 |
| repo_type | string | 否 | - | 显式指定仓库类型（github或gitlab）。如果不提供，将从URL自动检测 |
| output_dir | string | 否 | "output" | 输出目录 |
| include_patterns | array | 否 | 默认包含模式 | 包含的文件模式 |
| exclude_patterns | array | 否 | 默认排除模式 | 排除的文件模式 |
| max_file_size | integer | 否 | 100000 | 最大文件大小(字节) |
| language | string | 否 | "english" | 生成语言 |
| use_cache | boolean | 否 | true | 是否使用缓存 |
| max_abstractions | integer | 否 | 10 | 最大抽象概念数量 |

## 仓库类型说明

系统支持两种方式确定仓库类型：

1. **自动检测**（默认）：通过URL中的域名判断
   - 包含 `gitlab.com` 或 `gitlab.` 的URL会被识别为GitLab仓库
   - 其他URL会被识别为GitHub仓库

2. **显式指定**：使用 `repo_type` 参数
   - 值为 `github` 或 `gitlab`
   - 优先级高于自动检测
   - 适用于私有GitLab实例或自定义域名的GitLab仓库

### 使用场景示例：
- 私有GitLab实例：`https://gitlab.example.com/user/repo` + `repo_type: "gitlab"`
- 自定义域名GitHub：`https://code.example.com/user/repo` + `repo_type: "github"`

## 默认文件模式

### 包含模式
- 代码文件: `*.py`, `*.js`, `*.jsx`, `*.ts`, `*.tsx`, `*.go`, `*.java`
- 配置文件: `*.yaml`, `*.yml`, `*Dockerfile`, `*Makefile`
- 文档文件: `*.md`, `*.rst`

### 排除模式
- 资源目录: `assets/*`, `data/*`, `images/*`, `public/*`, `static/*`
- 测试目录: `*test*`, `*tests/*`, `*examples/*`
- 构建目录: `*dist/*`, `*build/*`, `*node_modules/*`
- 版本控制: `.git/*`, `.github/*`

## 使用示例

### 命令行使用

```bash
# 自动检测仓库类型（默认行为）
python main.py --repo https://github.com/username/repo

# 显式指定GitHub仓库类型
python main.py --repo https://custom-domain.com/user/repo --repo-type github

# 显式指定GitLab仓库类型（适用于私有GitLab实例）
python main.py --repo https://gitlab.example.com/user/repo --repo-type gitlab --gitlab-token your_token

# 使用本地目录
python main.py --dir /path/to/local/project
```

### 使用curl测试API

1. 启动生成任务：
```bash
curl -X POST "http://localhost:8000/generate-tutorial" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/repo",
    "language": "chinese",
    "max_abstractions": 8
  }'
```

2. 查询任务状态：
```bash
curl "http://localhost:8000/job/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

3. 下载结果：
```bash
curl -o tutorial.zip "http://localhost:8000/download/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### 使用Python客户端

```python
import requests
import json

# 启动生成任务
response = requests.post(
    "http://localhost:8000/generate-tutorial",
    json={
        "repo_url": "https://github.com/username/repo",
        "language": "chinese"
    }
)
job_id = response.json()["job_id"]

# 轮询任务状态
while True:
    status_response = requests.get(f"http://localhost:8000/job/{job_id}")
    status = status_response.json()
    if status["status"] in ["completed", "failed"]:
        break
    time.sleep(5)

# 下载结果
if status["status"] == "completed":
    download_response = requests.get(f"http://localhost:8000/download/{job_id}")
    with open("tutorial.zip", "wb") as f:
        f.write(download_response.content)
```

## 注意事项

1. 确保设置了必要的环境变量（如GITHUB_TOKEN、GITLAB_TOKEN）
2. 对于大型仓库，生成过程可能需要较长时间
3. API使用异步处理，返回的是任务ID而非即时结果
4. 生成的文件会保存在指定的输出目录中
5. 建议在生产环境中使用进程管理器（如systemd, supervisord）来管理服务
6. Ollama配置：
   - 默认使用 `qwen3:8b` 模型
   - 可通过 `OLLAMA_MODEL` 环境变量指定其他模型
   - 可通过 `OLLAMA_HOST` 环境变量指定Ollama服务地址
   - 确保Ollama服务已启动并运行在指定地址