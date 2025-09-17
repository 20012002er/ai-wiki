#!/usr/bin/env python3
"""
下载Swagger UI静态资源文件用于离线环境
"""
import os
import requests
import shutil

def download_file(url, local_path):
    """下载文件到本地"""
    print(f"下载: {url} -> {local_path}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def main():
    # 创建静态文件目录
    static_dir = "static/docs"
    os.makedirs(static_dir, exist_ok=True)
    
    # Swagger UI资源文件
    swagger_files = {
        "swagger-ui-bundle.js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        "swagger-ui-standalone-preset.js": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js",
        "swagger-ui.css": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        "favicon-32x32.png": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/favicon-32x32.png",
        "favicon-16x16.png": "https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/favicon-16x16.png"
    }
    
    # 下载所有文件
    for filename, url in swagger_files.items():
        local_path = os.path.join(static_dir, filename)
        download_file(url, local_path)
    
    # 创建自定义的index.html
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tutorial Generation API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="/static/docs/swagger-ui.css" />
    <link rel="icon" type="image/png" href="/static/docs/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="/static/docs/favicon-16x16.png" sizes="16x16" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *, *:before, *:after {
            box-sizing: inherit;
        }
        body {
            margin: 0;
            background: #fafafa;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="/static/docs/swagger-ui-bundle.js"></script>
    <script src="/static/docs/swagger-ui-standalone-preset.js"></script>
    <script>
    window.onload = function() {
        const ui = SwaggerUIBundle({
            url: "/openapi.json",
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIStandalonePreset
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout"
        });
        window.ui = ui;
    }
    </script>
</body>
</html>"""
    
    with open(os.path.join(static_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    
    print("Swagger UI静态资源下载完成！")

if __name__ == "__main__":
    main()