import requests
import base64
import os
import tempfile
import git
import time
import fnmatch
from typing import Union, Set, List, Dict, Tuple, Any
from urllib.parse import urlparse

def crawl_gitlab_files(
    repo_url, 
    token=None, 
    gitlab_domain="gitlab.com",  # 可配置的 GitLab 域名
    max_file_size: int = 1 * 1024 * 1024,  # 1 MB
    use_relative_paths: bool = False,
    include_patterns: Union[str, Set[str]] = None,
    exclude_patterns: Union[str, Set[str]] = None
):
    """
    Crawl files from a specific path in a GitLab repository at a specific commit.

    Args:
        repo_url (str): URL of the GitLab repository with specific path and commit
                        (e.g., 'https://gitlab.com/username/project/tree/main/src')
        token (str, optional): **GitLab personal access token.**
            - **Required for private repositories.**
            - **Recommended for private repos to avoid access issues.**
            - Can be passed explicitly or set via the `GITLAB_TOKEN` environment variable.
        gitlab_domain (str, optional): GitLab instance domain (default: "gitlab.com")
        max_file_size (int, optional): Maximum file size in bytes to download (default: 1 MB)
        use_relative_paths (bool, optional): If True, file paths will be relative to the specified subdirectory
        include_patterns (str or set of str, optional): Pattern or set of patterns specifying which files to include (e.g., "*.py", {"*.md", "*.txt"}).
                                                       If None, all files are included.
        exclude_patterns (str or set of str, optional): Pattern or set of patterns specifying which files to exclude.
                                                       If None, no files are excluded.

    Returns:
        dict: Dictionary with files and statistics
    """
    # Convert single pattern to set
    if include_patterns and isinstance(include_patterns, str):
        include_patterns = {include_patterns}
    if exclude_patterns and isinstance(exclude_patterns, str):
        exclude_patterns = {exclude_patterns}

    def should_include_file(file_path: str, file_name: str) -> bool:
        """Determine if a file should be included based on patterns"""
        # If no include patterns are specified, include all files
        if not include_patterns:
            include_file = True
        else:
            # Check if file matches any include pattern
            include_file = any(fnmatch.fnmatch(file_name, pattern) for pattern in include_patterns)

        # If exclude patterns are specified, check if file should be excluded
        if exclude_patterns and include_file:
            # Exclude if file matches any exclude pattern
            exclude_file = any(fnmatch.fnmatch(file_path, pattern) for pattern in exclude_patterns)
            return not exclude_file

        return include_file

    # Detect SSH URL (git@ or .git suffix)
    is_ssh_url = repo_url.startswith("git@") or repo_url.endswith(".git")

    if is_ssh_url:
        # Clone repo via SSH to temp dir
        with tempfile.TemporaryDirectory() as tmpdirname:
            print(f"Cloning SSH repo {repo_url} to temp dir {tmpdirname} ...")
            try:
                repo = git.Repo.clone_from(repo_url, tmpdirname)
            except Exception as e:
                print(f"Error cloning repo: {e}")
                return {"files": {}, "stats": {"error": str(e)}}

            # Attempt to checkout specific commit/branch if in URL
            # Parse ref and subdir from SSH URL? SSH URLs don't have branch info embedded
            # So rely on default branch, or user can checkout manually later
            # Optionally, user can pass ref explicitly in future API

            # Walk directory
            files = {}
            skipped_files = []

            for root, dirs, filenames in os.walk(tmpdirname):
                for filename in filenames:
                    abs_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(abs_path, tmpdirname)

                    # Check file size
                    try:
                        file_size = os.path.getsize(abs_path)
                    except OSError:
                        continue

                    if file_size > max_file_size:
                        skipped_files.append((rel_path, file_size))
                        print(f"Skipping {rel_path}: size {file_size} exceeds limit {max_file_size}")
                        continue

                    # Check include/exclude patterns
                    if not should_include_file(rel_path, filename):
                        print(f"Skipping {rel_path}: does not match include/exclude patterns")
                        continue

                    # Read content
                    try:
                        with open(abs_path, "r", encoding="utf-8-sig") as f:
                            content = f.read()
                        files[rel_path] = content
                        print(f"Added {rel_path} ({file_size} bytes)")
                    except Exception as e:
                        print(f"Failed to read {rel_path}: {e}")

            return {
                "files": files,
                "stats": {
                    "downloaded_count": len(files),
                    "skipped_count": len(skipped_files),
                    "skipped_files": skipped_files,
                    "base_path": None,
                    "include_patterns": include_patterns,
                    "exclude_patterns": exclude_patterns,
                    "source": "ssh_clone"
                }
            }

    # Parse GitLab URL to extract namespace, project, branch/commit, and path
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitLab URL: {repo_url}")
    
    # Extract the basic components - namespace and project
    namespace = path_parts[0]
    project = path_parts[1]
    
    # Setup for GitLab API
    headers = {"Content-Type": "application/json"}
    if token:
        headers["PRIVATE-TOKEN"] = token

    def fetch_branches(namespace: str, project: str):
        """Get branches of the repository"""

        url = f"https://{gitlab_domain}/api/v4/projects/{namespace}%2F{project}/repository/branches"
        response = requests.get(url, headers=headers, timeout=(30, 30))

        if response.status_code == 404:
            if not token:
                print(f"Error 404: Repository not found or is private.\n"
                      f"If this is a private repository, please provide a valid GitLab token via the 'token' argument or set the GITLAB_TOKEN environment variable.")
            else:
                print(f"Error 404: Repository not found or insufficient permissions with the provided token.\n"
                      f"Please verify the repository exists and the token has access to this repository.")
            return []
            
        if response.status_code != 200:
            print(f"Error fetching the branches of {namespace}/{project}: {response.status_code} - {response.text}")
            return []

        return response.json()

    def check_commit(namespace: str, project: str, commit_sha: str):
        """Check if a commit exists in the repository"""

        url = f"https://{gitlab_domain}/api/v4/projects/{namespace}%2F{project}/repository/commits/{commit_sha}"
        response = requests.get(url, headers=headers, timeout=(30, 30))

        return True if response.status_code == 200 else False

    # Check if URL contains a specific branch/commit
    ref = None
    specific_path = ""
    
    if len(path_parts) > 2 and 'tree' == path_parts[2]:
        join_parts = lambda i: '/'.join(path_parts[i:])

        branches = fetch_branches(namespace, project)
        branch_names = [branch.get("name") for branch in branches]

        # Fetching branches is not successful
        if len(branches) == 0:
            return {"files": {}, "stats": {"error": "Failed to fetch branches"}}

        # To check branch name
        relevant_path = join_parts(3)

        # Find a match with relevant path and get the branch name
        ref = next((name for name in branch_names if relevant_path.startswith(name)), None)

        # If match is not found, check if it's a commit SHA
        if ref is None:
            # Check if the next part looks like a commit SHA (40 char hex)
            potential_commit = path_parts[3]
            if len(potential_commit) == 40 and all(c in '0123456789abcdef' for c in potential_commit.lower()):
                if check_commit(namespace, project, potential_commit):
                    ref = potential_commit

        # If it is neither a branch nor a commit
        if ref is None:
            print(f"The given path does not match with any branch or commit in the repository.\n"
                  f"Please verify the path exists.")
            return {"files": {}, "stats": {"error": "Invalid branch or commit reference"}}

        # Combine all parts after the ref as the path
        part_index = 5 if '/' in ref else 4
        specific_path = join_parts(part_index) if part_index < len(path_parts) else ""
    else:
        # Don't put the ref param to query
        # and let GitLab decide default branch
        ref = None
        specific_path = ""
    
    # Dictionary to store path -> content mapping
    files = {}
    skipped_files = []
    
    def fetch_contents(path):
        """Fetch contents of the repository at a specific path and ref"""
        # URL encode the path for GitLab API
        encoded_path = requests.utils.quote(path, safe='') if path else ""
        url = f"https://{gitlab_domain}/api/v4/projects/{namespace}%2F{project}/repository/tree"
        params = {"path": encoded_path, "recursive": True, "ref": ref} if ref else {"path": encoded_path, "recursive": True}
        
        response = requests.get(url, headers=headers, params=params, timeout=(30, 30))
        
        if response.status_code == 429:  # Rate limiting
            reset_time = int(response.headers.get('RateLimit-Reset', 0))
            wait_time = max(reset_time - time.time(), 0) + 1
            print(f"Rate limit exceeded. Waiting for {wait_time:.0f} seconds...")
            time.sleep(wait_time)
            return fetch_contents(path)
            
        if response.status_code == 404:
            if not token:
                print(f"Error 404: Repository not found or is private.\n"
                      f"If this is a private repository, please provide a valid GitLab token via the 'token' argument or set the GITLAB_TOKEN environment variable.")
            else:
                print(f"Error 404: Path '{path}' not found in repository or insufficient permissions with the provided token.\n"
                      f"Please verify the token has access to this repository and the path exists.")
            return
            
        if response.status_code != 200:
            print(f"Error fetching {path}: {response.status_code} - {response.text}")
            return
        
        contents = response.json()
        
        for item in contents:
            item_path = item["path"]
            item_type = item["type"]  # tree (directory) or blob (file)
            
            # Calculate relative path if requested
            if use_relative_paths and specific_path:
                # Make sure the path is relative to the specified subdirectory
                if item_path.startswith(specific_path):
                    rel_path = item_path[len(specific_path):].lstrip('/')
                else:
                    rel_path = item_path
            else:
                rel_path = item_path
            
            if item_type == "blob":  # File
                # Check if file should be included based on patterns
                if not should_include_file(rel_path, os.path.basename(item_path)):
                    print(f"Skipping {rel_path}: Does not match include/exclude patterns")
                    continue
                
                # Get file content using GitLab API
                file_url = f"https://{gitlab_domain}/api/v4/projects/{namespace}%2F{project}/repository/files/{requests.utils.quote(item_path, safe='')}/raw"
                file_params = {"ref": ref} if ref else {}
                
                file_response = requests.get(file_url, headers=headers, params=file_params, timeout=(30, 30))
                
                if file_response.status_code == 200:
                    # Check content length
                    content_length = len(file_response.content)
                    if content_length > max_file_size:
                        skipped_files.append((item_path, content_length))
                        print(f"Skipping {rel_path}: File size ({content_length} bytes) exceeds limit ({max_file_size} bytes)")
                        continue
                    
                    try:
                        content = file_response.text
                        files[rel_path] = content
                        print(f"Downloaded: {rel_path} ({content_length} bytes)")
                    except UnicodeDecodeError:
                        # Handle binary files or encoding issues
                        print(f"Skipping {rel_path}: Binary file or encoding issue")
                        continue
                else:
                    print(f"Failed to download {rel_path}: {file_response.status_code}")
            
            elif item_type == "tree":  # Directory
                # Check if directory should be excluded before recursing
                if exclude_patterns:
                    dir_excluded = any(fnmatch.fnmatch(item_path, pattern) or
                                    fnmatch.fnmatch(rel_path, pattern) for pattern in exclude_patterns)
                    if dir_excluded:
                        continue
                
                # Only recurse if directory is not excluded
                fetch_contents(item_path)
    
    # Start crawling from the specified path
    fetch_contents(specific_path)
    
    return {
        "files": files,
        "stats": {
            "downloaded_count": len(files),
            "skipped_count": len(skipped_files),
            "skipped_files": skipped_files,
            "base_path": specific_path if use_relative_paths else None,
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
            "gitlab_domain": gitlab_domain
        }
    }

# Example usage
if __name__ == "__main__":
    # Get token from environment variable (recommended for private repos)
    gitlab_token = os.environ.get("GITLAB_TOKEN")
    if not gitlab_token:
        print("Warning: No GitLab token found in environment variable 'GITLAB_TOKEN'.\n"
              "Private repositories will not be accessible without a token.\n"
              "To access private repos, set the environment variable or pass the token explicitly.")
    
    # Example with custom GitLab domain
    repo_url = "https://your-gitlab-domain.com/username/project/tree/main/src"
    
    # Example: Get Python and Markdown files
    result = crawl_gitlab_files(
        repo_url, 
        token=gitlab_token,
        gitlab_domain="your-gitlab-domain.com",  # 自定义 GitLab 域名
        max_file_size=1 * 1024 * 1024,  # 1 MB in bytes
        use_relative_paths=True,  # Enable relative paths
        include_patterns={"*.py", "*.md"},  # Include Python and Markdown files
    )
    
    if result:
        files = result["files"]
        stats = result["stats"]
        
        print(f"\nDownloaded {stats['downloaded_count']} files.")
        print(f"Skipped {stats['skipped_count']} files due to size limits or patterns.")
        print(f"Base path for relative paths: {stats['base_path']}")
        print(f"GitLab domain: {stats['gitlab_domain']}")
        print(f"Include patterns: {stats['include_patterns']}")
        print(f"Exclude patterns: {stats['exclude_patterns']}")
        
        # Display all file paths in the dictionary
        print("\nFiles in dictionary:")
        for file_path in sorted(files.keys()):
            print(f"  {file_path}")
        
        # Example: accessing content of a specific file
        if files:
            sample_file = next(iter(files))
            print(f"\nSample file: {sample_file}")
            print(f"Content preview: {files[sample_file][:200]}...")