import base64
import re
import requests
from typing import List, Dict, Any, Optional, Tuple
from github import Github, GithubException
from bs4 import BeautifulSoup
import urllib.parse

from app.config import settings
from app.models import FileInfo
from app.services.code_extractor import TreeSitterExtractor, CodeFeatures, features_to_dict



class GitHubService:
    
    def __init__(self):
        if settings.github_token:
            self.github = Github(settings.github_token)
            self.authenticated = True
            print("Authenticated GitHub access enabled")
        else:
            self.github = Github()
            self.authenticated = False
        
        self.session = requests.Session()
        self.code_extractor = TreeSitterExtractor()  # Initialize code extractor
    
    async def get_repo_structure(self, owner: str, repo: str, branch: str = "main") -> Dict[str, Any]:
        try:
            print(f"Getting repo structure for {owner}/{repo} on branch {branch}")
            
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            headers = {}
            if settings.github_token:
                headers['Authorization'] = f'token {settings.github_token}'
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            tree_data = response.json()
            
            files = []
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob': 
                    download_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{item['path']}"
                    
                    file_info = FileInfo(
                        path=item['path'],
                        name=item['path'].split('/')[-1],
                        size=item.get('size', 0),
                        download_url=download_url,
                        ignore=False,
                    )
                    print(f'"{item['path']}", ',end="")
                    files.append(file_info)
            
            print(f"Total files fetched: {len(files)}")
            
            total_files = len(files)
            total_size = sum(f.size for f in files)
            
            
            structure = {
                "languages": self._detect_languages(files),
            }

            
            
            return {
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "total_files": total_files,
                "total_size": total_size,
                "files": files,
                "summary": structure,
            }
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 403:
                    print(f"GitHub API rate limit exceeded for {owner}/{repo}")
                    return {"error": "GitHub API rate limit exceeded"}
                elif e.response.status_code == 401:
                    print(f"GitHub API authentication failed for {owner}/{repo}")
                    return {"error": "GitHub API authentication failed"}
                elif e.response.status_code == 404:
                    print(f"Repository or branch not found for {owner}/{repo} on branch {branch}")
                    return {"error": "Repository or branch not found"}
            
            print(f"GitHub Trees API error for {owner}/{repo}")
            return {"error": "GitHub API error" }
        except Exception as e:
            print(f"Unexpected error for {owner}/{repo}")
            print(str(e))
            return {"error": "Unexpected error"}
    
    
    def _detect_languages(self, files: List[FileInfo]) -> Dict[str, int]:
        """Detect programming languages used in the repository"""
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.cs': 'C#',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sql': 'SQL',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS',
            '.vue': 'Vue',
            '.toml': 'TOML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML'
        }
        
        languages = {}
        for file_info in files:
            ext = '.' + file_info.name.split('.')[-1] if '.' in file_info.name else ''
            if ext in language_extensions:
                lang = language_extensions[ext]
                languages[lang] = languages.get(lang, 0) + 1
        
        return languages
    
    
    async def download_file_content(self, owner: str, repo: str, file_path: str, branch: str = "main") -> Optional[str]:
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
            '.go', '.rs', '.rb', '.php', '.cs', '.swift', '.kt', '.scala', '.r',
            '.sql', '.html', '.css', '.scss', '.less', '.vue', '.toml', '.yaml',
            '.yml', '.json', '.xml', '.md', '.txt', '.sh', '.bat', '.ps1', '.pl',
            '.lua', '.dart', '.ex', '.exs', '.elm', '.clj', '.cljs', '.hs', '.ml',
            '.fs', '.vb', '.pas', '.asm', '.s', '.m', '.mm', '.gradle', '.pom',
            '.cmake', '.make', '.dockerfile', '.tf', '.hcl', '.proto'
        }
        
        file_ext = '.' + file_path.split('.')[-1].lower() if '.' in file_path else ''
        if file_ext not in code_extensions:
            print(f"Skipping non-code file: {file_path}")
            return None
            
        try:
            repository = self.github.get_repo(f"{owner}/{repo}")
            file_content = repository.get_contents(file_path, ref=branch)
            return file_content.content
                
        except GithubException as e:
            if e.status in [403, 401]:
                print(f"GitHub API access issue, using fallback for {file_path}")
                return {"error": "GitHub API access issue" }
            else:
                print(f"Failed to download file via API")
                return {"error": "Failed to download file via API" }

        except UnicodeDecodeError:
            print(f"Binary file detected, skipping content for {file_path}")
            return None
        except Exception as e:
            print(f"Unexpected error, trying fallback for {file_path}", str(e))
            return {"error": "Unexpected error" }
    
    async def extract_code_features(self, owner: str, repo: str, file_path: str, branch: str = "main") -> Optional[Dict[str, Any]]:
        """
        Extract code features from a specific file using Tree-sitter.
        Returns extracted strings, function names, variables, comments, and docstrings.
        """
        try:
            file_content = await self.download_file_content(owner, repo, file_path, branch)
            if not file_content or isinstance(file_content, dict):
                return None
            
            try:
                decoded_content = base64.b64decode(file_content).decode('utf-8')
            except Exception as e:
                print(f"Failed to decode file content for {file_path}: {e}")
                return None
            
            language = self.code_extractor.detect_language(file_path)
            if not language:
                print(f"Unsupported language for file: {file_path}")
                return None
            
            features = self.code_extractor.extract_features(decoded_content, language, file_path)
            return features_to_dict(features)
            
        except Exception as e:
            print(f"Error extracting code features from {file_path}: {e}")
            return None
    
    def get_code_similarity_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate features specifically useful for code similarity and AI detection.
        Returns simplified feature vectors for comparison.
        """
        try:
            # Extract key identifiers for similarity analysis
            similarity_features = {
                'function_signature_patterns': [],
                'variable_naming_patterns': [],
                'string_patterns': [],
                'comment_patterns': [],
                'import_patterns': [],
                'code_structure_metrics': {}
            }
            
            aggregated = features.get('aggregated_features', {})
            
            # Function signature patterns (simplified)
            for func_name in aggregated.get('function_names', []):
                if len(func_name) > 2:  # Filter very short names
                    # Extract naming patterns
                    if '_' in func_name:
                        similarity_features['function_signature_patterns'].append('snake_case')
                    elif func_name[0].islower() and any(c.isupper() for c in func_name):
                        similarity_features['function_signature_patterns'].append('camelCase')
                    elif func_name[0].isupper():
                        similarity_features['function_signature_patterns'].append('PascalCase')
            
            # Variable naming patterns
            for var_name in aggregated.get('variable_names', []):
                if len(var_name) > 1:
                    if var_name.isupper():
                        similarity_features['variable_naming_patterns'].append('CONSTANT')
                    elif '_' in var_name:
                        similarity_features['variable_naming_patterns'].append('snake_case')
                    elif var_name[0].islower():
                        similarity_features['variable_naming_patterns'].append('camelCase')
            
            # String content patterns (anonymized)
            for string_val in aggregated.get('strings', []):
                if len(string_val) > 5:
                    # Categorize string types
                    if string_val.startswith('http'):
                        similarity_features['string_patterns'].append('url_pattern')
                    elif '@' in string_val:
                        similarity_features['string_patterns'].append('email_pattern')
                    elif string_val.isdigit():
                        similarity_features['string_patterns'].append('numeric_string')
                    elif len(string_val.split()) > 3:
                        similarity_features['string_patterns'].append('sentence_pattern')
            
            # Comment patterns
            for comment in aggregated.get('comments', []):
                comment_clean = comment.strip('#/* ').lower()
                if len(comment_clean) > 10:
                    if any(word in comment_clean for word in ['todo', 'fixme', 'hack']):
                        similarity_features['comment_patterns'].append('todo_comment')
                    elif any(word in comment_clean for word in ['copyright', 'license', 'author']):
                        similarity_features['comment_patterns'].append('header_comment')
                    else:
                        similarity_features['comment_patterns'].append('description_comment')
            
            # Import patterns
            for import_stmt in aggregated.get('imports', []):
                # Extract import types
                if 'numpy' in import_stmt or 'pandas' in import_stmt:
                    similarity_features['import_patterns'].append('data_science')
                elif 'flask' in import_stmt or 'django' in import_stmt:
                    similarity_features['import_patterns'].append('web_framework')
                elif 'requests' in import_stmt or 'urllib' in import_stmt:
                    similarity_features['import_patterns'].append('http_library')
            
            # Code structure metrics
            extraction_stats = features.get('extraction_stats', {})
            feature_counts = extraction_stats.get('feature_counts', {});
            
            similarity_features['code_structure_metrics'] = {
                'function_to_class_ratio': (
                    feature_counts.get('unique_functions', 0) / 
                    max(feature_counts.get('unique_classes', 1), 1)
                ),
                'comment_density': (
                    feature_counts.get('unique_comments', 0) / 
                    max(feature_counts.get('unique_functions', 1), 1)
                ),
                'import_diversity': len(set(similarity_features['import_patterns'])),
                'naming_consistency': {
                    'function_patterns': len(set(similarity_features['function_signature_patterns'])),
                    'variable_patterns': len(set(similarity_features['variable_naming_patterns']))
                }
            }
            
            # Deduplicate pattern lists
            for key in similarity_features:
                if isinstance(similarity_features[key], list):
                    similarity_features[key] = list(set(similarity_features[key]))
            
            return similarity_features
            
        except Exception as e:
            print(f"Error generating similarity features: {e}")
            return {}
    
    async def get_readme_content(self, owner: str, repo: str, branch: str = "main") -> Optional[str]:
        readme_files = [
            "README.md", "readme.md", "Readme.md", 
            "README.rst", "readme.rst", "Readme.rst",
            "README.txt", "readme.txt", "Readme.txt",
            "README", "readme"
        ]
        
        for readme_file in readme_files:
            try:
                repository = self.github.get_repo(f"{owner}/{repo}")
                file_content = repository.get_contents(readme_file, ref=branch)
                
                decoded_content = base64.b64decode(file_content.content).decode('utf-8')
                return decoded_content
                
            except GithubException as e:
                if e.status == 404:
                    continue
                else:
                    print(f"GitHub API error fetching {readme_file}: {e}")
                    continue
            except Exception as e:
                print(f"Error decoding {readme_file}: {e}")
                continue
        
        return None

    async def get_repository_commits(self, owner: str, repo: str, branch: str = "main", per_page: int = 100) -> Dict[str, Any]:
        limit = 25  # I want dont want to be spamming reqs on my key 😭
        truncated = False
        try:
            print(f"Getting commits for {owner}/{repo} on branch {branch}")
            
            url = f"https://api.github.com/repos/{owner}/{repo}/commits"
            headers = {}
            if settings.github_token:
                headers['Authorization'] = f'token {settings.github_token}'
            
            params = {
                'sha': branch,
                'per_page': min(per_page, 100)  # GitHub API max is 100
            }
            
            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            commits_data = response.json()
            commits = []
            with open(f"./commit_.json", "w") as f:
                    import json
                    json.dump(commits_data, f, indent=2)
            
            for i, commit_item in enumerate(commits_data):
                if i >= limit:
                    break
                    
                commit_sha = commit_item['sha']
                commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
                
                commit_response = self.session.get(commit_url, headers=headers)
                commit_response.raise_for_status()
                commit_detail = commit_response.json()
                
                files_changed = []
                total_additions = 0
                total_deletions = 0
                
                for file_change in commit_detail.get('files', []):
                    file_info = {
                        'filename': file_change['filename'],
                        'status': file_change['status'],
                        'additions': file_change.get('additions', 0),
                        'deletions': file_change.get('deletions', 0),
                        'changes': file_change.get('changes', 0)
                    }
                    files_changed.append(file_info)
                    total_additions += file_change.get('additions', 0)
                    total_deletions += file_change.get('deletions', 0)
                
                commit_info = {
                    'message': commit_detail['commit']['message'],
                    'author_name': commit_detail['commit']['author']['name'],
                    'date': commit_detail['commit']['author']['date'],
                    'files_changed': files_changed,
                    'total_additions': total_additions,
                    'total_deletions': total_deletions,
                    'total_files': len(files_changed)
                }
                
                commits.append(commit_info)
            else:
                if len(commits_data) > limit:
                    truncated = True
            
            return {
                'owner': owner,
                'repo': repo,
                'branch': branch,
                'commits': commits,
                'total_commits': len(commits_data),
                'truncated': truncated
            }
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed for {owner}/{repo}: {e}")
            raise Exception(f"Failed to fetch commits: {str(e)}")
        except Exception as e:
            print(f"Error getting commits for {owner}/{repo}: {e}")
            raise Exception(f"Failed to get repository commits: {str(e)}")
    
    async def get_total_commits_count(self, owner: str, repo: str, branch: str = "main") -> int:
        try:
            print(f"Getting total commits count for {owner}/{repo} on branch {branch}")
            
            url = f"https://api.github.com/repos/{owner}/{repo}/commits"
            params = {
                'sha': branch,
                'per_page': 1
            }
            headers = {'Accept': 'application/vnd.github+json'}
            if settings.github_token:
                headers['Authorization'] = f'token {settings.github_token}'
            
            response = self.session.head(url, params=params, headers=headers)
            response.raise_for_status()
            
            link_header = response.headers.get('Link')
            
            if not link_header:
                get_response = self.session.get(url, params=params, headers=headers)
                get_response.raise_for_status()
                commits_data = get_response.json()
                total_commits = len(commits_data) if commits_data else 0
                return total_commits
            
            last_page_match = re.search(r'<[^>]*page=(\d+)[^>]*>;\s*rel="last"', link_header)

            if last_page_match:
                total_commits = int(last_page_match.group(1))
                return total_commits
            else:
                return 1
                
        except requests.exceptions.RequestException as e:
            print(f"API request failed for {owner}/{repo}: {e}")
            raise Exception(f"Failed to fetch commits count: {str(e)}")
        except Exception as e:
            print(f"Error getting commits count for {owner}/{repo}: {e}")
            raise Exception(f"Failed to get repository commits count: {str(e)}")
