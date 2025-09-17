import os
import uuid
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import dotenv

# Import the existing flow and modules
from flow import create_tutorial_flow

dotenv.load_dotenv()

# Default file patterns (copied from main.py)
DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "*Dockerfile",
    "*Makefile", "*.yaml", "*.yml",
}

DEFAULT_EXCLUDE_PATTERNS = {
    "assets/*", "data/*", "images/*", "public/*", "static/*", "temp/*",
    "*docs/*",
    "*venv/*",
    "*.venv/*",
    "*test*",
    "*tests/*",
    "*examples/*",
    "v1/*",
    "*dist/*",
    "*build/*",
    "*experimental/*",
    "*deprecated/*",
    "*misc/*",
    "*legacy/*",
    ".git/*", ".github/*", ".next/*", ".vscode/*",
    "*obj/*",
    "*bin/*",
    "*node_modules/*",
    "*.log"
}

# Pydantic models for request/response
class TutorialRequest(BaseModel):
    repo_url: Optional[str] = Field(None, description="URL of the public GitHub or GitLab repository")
    local_dir: Optional[str] = Field(None, description="Path to local directory")
    project_name: Optional[str] = Field(None, description="Project name")
    github_token: Optional[str] = Field(None, description="GitHub personal access token")
    gitlab_token: Optional[str] = Field(None, description="GitLab personal access token")
    repo_type: Optional[str] = Field(None, description="Explicit repository type (github or gitlab). If not provided, will auto-detect from URL.")
    output_dir: str = Field("output", description="Base directory for output")
    include_patterns: Optional[List[str]] = Field(None, description="Include file patterns")
    exclude_patterns: Optional[List[str]] = Field(None, description="Exclude file patterns")
    max_file_size: int = Field(100000, description="Maximum file size in bytes")
    language: str = Field("english", description="Language for the generated tutorial")
    use_cache: bool = Field(True, description="Enable LLM response caching")
    max_abstractions: int = Field(10, description="Maximum number of abstractions to identify")

class TutorialResponse(BaseModel):
    job_id: str
    status: str
    message: str
    output_dir: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Global variables for job tracking
jobs: Dict[str, Dict[str, Any]] = {}
app = FastAPI(
    title="Tutorial Generation API",
    description="API for generating codebase tutorials",
    docs_url=None,  # Disable default docs to use custom implementation
    redoc_url=None  # Disable default redoc to use custom implementation
)

def run_tutorial_generation(job_id: str, request: TutorialRequest):
    """Background task to run tutorial generation"""
    try:
        jobs[job_id]["status"] = "running"
        
        # Convert request to shared dictionary format
        repo_type = None
        if request.repo_url:
            # Determine repository type: use explicit parameter if provided, otherwise auto-detect
            if request.repo_type:
                repo_type = request.repo_type
            else:
                # Auto-detect from URL (backward compatibility)
                is_gitlab = "gitlab.com" in request.repo_url or "gitlab." in request.repo_url
                repo_type = "gitlab" if is_gitlab else "github"
        
        shared = {
            "repo_url": request.repo_url,
            "local_dir": request.local_dir,
            "project_name": request.project_name,
            "github_token": request.github_token,
            "gitlab_token": request.gitlab_token,
            "repo_type": repo_type,  # Add repository type information
            "output_dir": request.output_dir,
            "include_patterns": set(request.include_patterns) if request.include_patterns else DEFAULT_INCLUDE_PATTERNS,
            "exclude_patterns": set(request.exclude_patterns) if request.exclude_patterns else DEFAULT_EXCLUDE_PATTERNS,
            "max_file_size": request.max_file_size,
            "language": request.language,
            "use_cache": request.use_cache,
            "max_abstraction_num": request.max_abstractions,
            "files": [],
            "abstractions": [],
            "relationships": {},
            "chapter_order": [],
            "chapters": [],
            "final_output_dir": None
        }

        # Create and run the flow
        tutorial_flow = create_tutorial_flow()
        result = tutorial_flow.run(shared)

        # Store the result
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = {
            "output_dir": shared.get("final_output_dir"),
            "files_generated": len(shared.get("chapters", [])),
            "abstractions_identified": len(shared.get("abstractions", []))
        }
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)

@app.post("/generate-tutorial", response_model=TutorialResponse)
async def generate_tutorial(request: TutorialRequest, background_tasks: BackgroundTasks):
    """Start a tutorial generation job"""
    # Validate that either repo_url or local_dir is provided
    if not request.repo_url and not request.local_dir:
        raise HTTPException(status_code=400, detail="Either repo_url or local_dir must be provided")
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job tracking
    jobs[job_id] = {
        "status": "queued",
        "request": request.dict(),
        "result": None,
        "error": None
    }
    
    # Start the background task
    background_tasks.add_task(run_tutorial_generation, job_id, request)
    
    return TutorialResponse(
        job_id=job_id,
        status="queued",
        message="Tutorial generation job started",
        output_dir=request.output_dir
    )

@app.get("/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get the status of a tutorial generation job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress={
            "step": "generating" if job["status"] == "running" else job["status"],
            "details": "Processing tutorial generation" if job["status"] == "running" else job["status"]
        },
        result=job.get("result"),
        error=job.get("error")
    )

@app.get("/download/{job_id}")
async def download_tutorial(job_id: str):
    """Download the generated tutorial files"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    output_dir = job["result"]["output_dir"]
    if not output_dir or not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail="Output directory not found")
    
    # Create a zip file of the output directory
    import zipfile
    import tempfile
    
    zip_filename = f"{job_id}_tutorial.zip"
    zip_path = os.path.join(tempfile.gettempdir(), zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=zip_filename
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "tutorial-generation-api"}

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", response_class=HTMLResponse)
async def custom_docs():
    """自定义Swagger UI文档页面（离线可用）"""
    try:
        with open("static/docs/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>API Documentation</h1><p>Swagger UI resources not found. Please check static file setup.</p>")

@app.get("/redoc", response_class=HTMLResponse)
async def custom_redoc():
    """自定义ReDoc文档页面（离线可用）"""
    redoc_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tutorial Generation API - Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #4990e2;
                padding-bottom: 10px;
            }
            .endpoint {
                margin: 20px 0;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: #fafafa;
            }
            .method {
                display: inline-block;
                padding: 4px 8px;
                background: #4990e2;
                color: white;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
            .path {
                font-family: monospace;
                font-size: 16px;
            }
            .description {
                margin-top: 10px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Tutorial Generation API Documentation</h1>
            <p>This is an offline-friendly API documentation page.</p>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <span class="path">/generate-tutorial</span>
                <div class="description">Start a tutorial generation job</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/job/{job_id}</span>
                <div class="description">Get the status of a tutorial generation job</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/download/{job_id}</span>
                <div class="description">Download the generated tutorial files</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/health</span>
                <div class="description">Health check endpoint</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">/openapi.json</span>
                <div class="description">OpenAPI specification</div>
            </div>
            
            <p>For interactive documentation, visit <a href="/docs">/docs</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=redoc_html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)