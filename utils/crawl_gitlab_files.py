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
    gitlab_domain=None,  # 可配置的 GitLab 域名
    gitlab_protocol=None,  # 可配置的 GitLab 协议
    max_file_size: int = 1 * 1024 * 1024,  # 1 MB
    use_relative_paths: bool = False,
    include_patterns: Union[str, Set[str]] = None,
    exclude_patterns: Union[str, Set[str]] = None,
    debug: bool = False,
    ref: str = None  # 用户指定的分支或commit引用
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
        gitlab_domain (str, optional): GitLab instance domain. If None, uses GITLAB_DOMAIN environment variable or defaults to "gitlab.com"
        gitlab_protocol (str, optional): GitLab instance protocol ("http" or "https"). If None, uses GITLAB_PROTOCOL environment variable or defaults to "https"
        max_file_size (int, optional): Maximum file size in bytes to download (default: 1 MB)
        use_relative_paths (bool, optional): If True, file paths will be relative to the specified subdirectory
        include_patterns (str or set of str, optional): Pattern or set of patterns specifying which files to include (e.g., "*.py", {"*.md", "*.txt"}).
                                                       If None, all files are included.
        exclude_patterns (str or set of str, optional): Pattern or set of patterns specifying which files to exclude.
                                                       If None, no files are excluded.
        debug (bool, optional): Enable debug mode for detailed logging. Useful for troubleshooting 400 errors.
        ref (str, optional): Specific branch, tag, or commit reference to use. If provided, will override any ref parsed from URL.

    Returns:
        dict: Dictionary with files and statistics
    """
    # Convert single pattern to set
    if include_patterns and isinstance(include_patterns, str):
        include_patterns = {include_patterns}
    if exclude_patterns and isinstance(exclude_patterns, str):
        exclude_patterns = {exclude_patterns}

    # Get GitLab configuration from environment variables with fallbacks
    if gitlab_domain is None:
        gitlab_domain = os.environ.get("GITLAB_DOMAIN", "gitlab.com")
    if gitlab_protocol is None:
        gitlab_protocol = os.environ.get("GITLAB_PROTOCOL", "https")
    
    # Validate protocol
    if gitlab_protocol not in ("http", "https"):
        gitlab_protocol = "https"  # Default to HTTPS if invalid

    if token is None:
        token = os.environ.get("GITLAB_TOKEN")
        if token is None:
            print("Warning: No GitLab token provided. Private repositories may not be accessible.\n"
                  "To access private repos, provide a token via the 'token' argument or set the GITLAB_TOKEN environment variable.")
    
    # Construct base URL for API calls
    gitlab_base_url = f"{gitlab_protocol}://{gitlab_domain}"
    
    if debug:
        print(f"DEBUG: GitLab base URL: {gitlab_base_url}")
        print(f"DEBUG: Token provided: {'Yes' if token else 'No'}")
        if token:
            print(f"DEBUG: Token length: {len(token)} characters")
        print(f"DEBUG: Repository URL: {repo_url}")
        # Namespace and project will be parsed later, so we can't print them here yet

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
        # Convert SSH URL to HTTP URL for API access instead of cloning
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
                print(f"Warning: Unable to parse SSH URL: {repo_url}. Falling back to API detection.")
        elif repo_url.endswith(".git"):
            # Remove .git suffix for cleaner API usage
            repo_url = repo_url[:-4]
            print(f"Removed .git suffix: {repo_url}")
        
        # Re-parse the URL after conversion
        parsed_url = urlparse(repo_url)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError(f"Invalid GitLab URL after SSH conversion: {repo_url}")
        
        # Extract the basic components - namespace and project
        namespace = path_parts[0]
        project = path_parts[1]
        
        print(f"Using API access instead of SSH cloning for better authentication support")

    # Parse GitLab URL to extract namespace, project, branch/commit, and path
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitLab URL: {repo_url}")
    
    # Extract the basic components - namespace and project
    namespace = path_parts[0]
    project = path_parts[1]
    
    if debug:
        print(f"DEBUG: Parsed namespace: {namespace}, project: {project}")
    
    # Setup for GitLab API
    headers = {"Content-Type": "application/json"}
    if token:
        headers["PRIVATE-TOKEN"] = token
        if debug:
            print(f"DEBUG: Using PRIVATE-TOKEN header for authentication")

    def fetch_branches(namespace: str, project: str):
        """Get branches of the repository"""

        # Properly encode project name for branches API
        encoded_project = requests.utils.quote(project, safe='')
        url = f"{gitlab_base_url}/api/v4/projects/{namespace}%2F{encoded_project}/repository/branches"
        if debug:
            print(f"DEBUG: Fetching branches from URL: {url}")
            
        response = requests.get(url, headers=headers, timeout=(30, 30))
        
        if debug:
            print(f"DEBUG: Branches response status: {response.status_code}")

        if response.status_code == 404:
            if not token:
                print(f"Error 404: Repository not found or is private.\n"
                      f"If this is a private repository, please provide a valid GitLab token via the 'token' argument or set the GITLAB_TOKEN environment variable.")
            else:
                print(f"Error 404: Repository not found or insufficient permissions with the provided token.\n"
                      f"Please verify the repository exists and the token has access to this repository.")
            return []
            
        if response.status_code == 400:
            print(f"Error 400: Bad Request when fetching branches of {namespace}/{project}.\n"
                  f"This may indicate:\n"
                  f"1. Invalid project path encoding\n"
                  f"2. GitLab API compatibility issue\n"
                  f"Response: {response.text[:200]}...")
            return []
        elif response.status_code != 200:
            print(f"Error fetching the branches of {namespace}/{project}: {response.status_code} - {response.text[:200]}...")
            return []

        return response.json()

    def check_commit(namespace: str, project: str, commit_sha: str):
        """Check if a commit exists in the repository"""

        # Properly encode project name for commits API
        encoded_project = requests.utils.quote(project, safe='')
        url = f"{gitlab_base_url}/api/v4/projects/{namespace}%2F{encoded_project}/repository/commits/{commit_sha}"
        if debug:
            print(f"DEBUG: Checking commit at URL: {url}")
            
        response = requests.get(url, headers=headers, timeout=(30, 30))
        
        if debug:
            print(f"DEBUG: Commit check response status: {response.status_code}")
        
        if response.status_code == 400:
            print(f"Error 400: Bad Request when checking commit {commit_sha}.\n"
                  f"This may indicate invalid commit SHA format or encoding issue.")
            return False
            
        return True if response.status_code == 200 else False

    # Check if user provided a specific ref, otherwise parse from URL
    specific_path = ""
    
    # If user provided a ref, use it directly
    if ref:
        if debug:
            print(f"DEBUG: Using user-provided ref: {ref}")
        
        # Check if URL contains a specific path after the ref
        if len(path_parts) > 3 and 'tree' == path_parts[3]:
            join_parts = lambda i: '/'.join(path_parts[i:])
            # Path format: namespace/project/-/tree/ref/path
            # So we start from index 5 (after ref)
            part_index = 5
            specific_path = join_parts(part_index) if part_index < len(path_parts) else ""
    else:
        # Fallback to original URL parsing logic if no ref provided
        if len(path_parts) > 3 and 'tree' == path_parts[3]:
            join_parts = lambda i: '/'.join(path_parts[i:])

            branches = fetch_branches(namespace, project)
            branch_names = [branch.get("name") for branch in branches]

            # Fetching branches is not successful
            if len(branches) == 0:
                return {"files": {}, "stats": {"error": "Failed to fetch branches"}}

            # To check branch name
            relevant_path = join_parts(4)

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
            # Path format: namespace/project/-/tree/ref/path
            # So we start from index 5 (after ref)
            part_index = 5
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
        # URL encode the path for GitLab API - GitLab requires proper encoding
        # Use double URL encoding for special characters in paths
        encoded_path = requests.utils.quote(path, safe='') if path else ""
        double_encoded_path = requests.utils.quote(encoded_path, safe='') if path else ""
        
        # GitLab API expects proper encoding for project names with special characters
        encoded_project = requests.utils.quote(project, safe='')
        url = f"{gitlab_base_url}/api/v4/projects/{namespace}%2F{encoded_project}/repository/tree"
        
        # Build parameters carefully - GitLab can be sensitive to parameter format
        params = {}
        if path:
            params["path"] = encoded_path  # GitLab expects single encoding for path parameter
        params["recursive"] = True
        if ref:
            params["ref"] = ref
            
        if debug:
            print(f"DEBUG: Fetching tree for path '{path}' with params: {params}")
            print(f"DEBUG: Tree request URL: {url}")
            
        response = requests.get(url, headers=headers, params=params, timeout=(30, 30))
        
        if debug:
            print(f"DEBUG: Tree response status: {response.status_code}")
        
        if response.status_code == 429:  # Rate limiting
            reset_time = int(response.headers.get('RateLimit-Reset', 0))
            wait_time = max(reset_time - time.time(), 0) + 1
            print(f"Rate limit exceeded. Waiting for {wait_time:.0f} seconds...")
            time.sleep(wait_time)
            return fetch_contents(path)
            
        if response.status_code == 404:
            if not token:
                print(f"Error 404: Repository not found or is private.\n"
                      f"If this is a private repository, please provide a valid GitLab token via the 'token' argument or set the GITLAB_TOKEN environment variable.\n"
                      f"For custom GitLab instances, also ensure GITLAB_DOMAIN and GITLAB_PROTOCOL environment variables are set correctly.")
            else:
                print(f"Error 404: Path '{path}' not found in repository or insufficient permissions with the provided token.\n"
                      f"Please verify:\n"
                      f"1. The token has access to this repository\n"
                      f"2. The path exists in the repository\n"
                      f"3. For custom GitLab instances: GITLAB_DOMAIN and GITLAB_PROTOCOL are set correctly")
            return
            
        if response.status_code == 401:
            print(f"Error 401: Authentication failed.\n"
                  f"Please verify your GitLab token is valid and has appropriate permissions.\n"
                  f"For custom GitLab instances, ensure GITLAB_DOMAIN and GITLAB_PROTOCOL are set correctly.")
            return
            
        if response.status_code == 403:
            print(f"Error 403: Access forbidden.\n"
                  f"Your token may not have sufficient permissions for this repository.\n"
                  f"Please verify the token has at least 'read_repository' scope.")
            return
            
        if response.status_code == 400:
            print(f"Error 400: Bad Request when fetching {path}.\n"
                  f"This may indicate:\n"
                  f"1. Invalid path encoding: {encoded_path}\n"
                  f"2. Invalid ref parameter: {ref}\n"
                  f"3. GitLab API compatibility issue\n"
                  f"Response: {response.text[:200]}...")
            return
        elif response.status_code != 200:
            print(f"Error fetching {path}: {response.status_code} - {response.text[:200]}...")
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
                
                # Get file content using GitLab API - ensure proper encoding
                encoded_item_path = requests.utils.quote(item_path, safe='')
                encoded_project = requests.utils.quote(project, safe='')
                file_url = f"{gitlab_base_url}/api/v4/projects/{namespace}%2F{encoded_project}/repository/files/{encoded_item_path}/raw"
                
                file_params = {}
                if ref:
                    file_params["ref"] = ref
                    
                if debug:
                    print(f"DEBUG: Downloading file: {item_path}")
                    print(f"DEBUG: File URL: {file_url}")
                    print(f"DEBUG: File params: {file_params}")
                
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
                    if file_response.status_code == 400:
                        print(f"Failed to download {rel_path}: Bad Request (400). This may indicate:\n"
                              f"1. Invalid file path encoding\n"
                              f"2. Invalid ref parameter\n"
                              f"3. GitLab API compatibility issue\n"
                              f"Response: {file_response.text[:200]}...")
                    elif file_response.status_code == 401:
                        print(f"Failed to download {rel_path}: Authentication failed (401). Please verify your GitLab token.")
                    elif file_response.status_code == 403:
                        print(f"Failed to download {rel_path}: Access forbidden (403). Token may lack sufficient permissions.")
                    elif file_response.status_code == 404:
                        print(f"Failed to download {rel_path}: File not found (404).")
                    else:
                        print(f"Failed to download {rel_path}: {file_response.status_code} - {file_response.text[:100]}...")
            
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
            "gitlab_domain": gitlab_domain,
            "gitlab_protocol": gitlab_protocol
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
        gitlab_protocol="https",  # 自定义 GitLab 协议
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
        print(f"GitLab protocol: {stats['gitlab_protocol']}")
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