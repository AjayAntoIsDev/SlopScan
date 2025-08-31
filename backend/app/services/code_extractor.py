import tree_sitter
from tree_sitter import Language, Parser, Node
import os
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class CodeFeatures:
    strings: List[str]
    function_names: List[str]
    variable_names: List[str]
    comments: List[str]
    docstrings: List[str]
    class_names: List[str]
    method_names: List[str]
    imports: List[str]
    language: str
    file_path: Optional[str] = None


class TreeSitterExtractor:
    """Tree-sitter based code feature extractor."""
    
    def __init__(self):
        self.parsers = {}
        self.languages = {}
        self._init_languages()
    
    def _init_languages(self):
        """Initialize Tree-sitter parsers for supported languages."""
        lang_mappings = {
            'python': 'tree_sitter_python',
            'javascript': 'tree_sitter_javascript', 
            'java': 'tree_sitter_java',
            'cpp': 'tree_sitter_cpp',
            'c': 'tree_sitter_c',
            'go': 'tree_sitter_go',
            'rust': 'tree_sitter_rust',
            'ruby': 'tree_sitter_ruby',
            'php': 'tree_sitter_php'
        }
        
        for lang_name, module_name in lang_mappings.items():
            try:
                language_module = __import__(module_name)
                language_func = None
                
                if lang_name == 'php':
                    if hasattr(language_module, 'language_php'):
                        language_func = getattr(language_module, 'language_php')
                    elif hasattr(language_module, 'language_php_only'):
                        language_func = getattr(language_module, 'language_php_only')
                else:
                    for func_name in ['language', f'language_{lang_name}', 'get_language']:
                        if hasattr(language_module, func_name):
                            language_func = getattr(language_module, func_name)
                            break
                
                if language_func is None:
                    # Debug: show available functions in the module
                    available_funcs = [attr for attr in dir(language_module) if callable(getattr(language_module, attr)) and not attr.startswith('_')]
                    print(f"Warning: Could not find language function in {module_name}")
                    print(f"Available functions: {available_funcs}")
                    continue
                
                language = Language(language_func())
                parser = Parser(language)
                
                self.languages[lang_name] = language
                self.parsers[lang_name] = parser
                
            except ImportError:
                print(f"Warning: {module_name} not available, skipping {lang_name}")
                print(f"Install with: pip install {module_name.replace('_', '-')}")
            except Exception as e:
                print(f"Error initializing {lang_name}: {e}")
        
        try:
            import tree_sitter_typescript
            
            typescript_language = Language(tree_sitter_typescript.language_typescript())
            typescript_parser = Parser(typescript_language)
            self.languages['typescript'] = typescript_language
            self.parsers['typescript'] = typescript_parser
            
            tsx_language = Language(tree_sitter_typescript.language_tsx())
            tsx_parser = Parser(tsx_language)
            self.languages['tsx'] = tsx_language
            self.parsers['tsx'] = tsx_parser
            
        except ImportError:
            print("Warning: tree_sitter_typescript not available, skipping typescript and tsx")
            print("Install with: pip install tree-sitter-typescript")
        except Exception as e:
            print(f"Error initializing TypeScript/TSX: {e}")
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension."""
        ext_to_lang = {
            '.py': 'python',
            '.js': 'javascript', 
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'tsx',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        suffix = Path(file_path).suffix.lower()
        return ext_to_lang.get(suffix)
    
    def extract_features(self, code: str, language: str, file_path: Optional[str] = None) -> CodeFeatures:
        if language not in self.parsers:
            print("Language not supported by Tree-sitter, using fallback extraction.")
            return self._fallback_extraction(code, language, file_path)
        
        parser = self.parsers[language]
        tree = parser.parse(bytes(code, 'utf8'))
        
        features = CodeFeatures(
            strings=[],
            function_names=[],
            variable_names=[],
            comments=[],
            docstrings=[],
            class_names=[],
            method_names=[],
            imports=[],
            language=language,
            file_path=file_path
        )
        
        if language == 'python':
            self._extract_python_features(tree.root_node, code, features)
        elif language in ['javascript', 'typescript', 'tsx']:
            self._extract_js_ts_features(tree.root_node, code, features)
        elif language == 'java':
            self._extract_java_features(tree.root_node, code, features)
        elif language in ['c', 'cpp']:
            self._extract_c_cpp_features(tree.root_node, code, features)
        elif language == 'go':
            self._extract_go_features(tree.root_node, code, features)
        elif language == 'rust':
            self._extract_rust_features(tree.root_node, code, features)
        elif language == 'ruby':
            self._extract_ruby_features(tree.root_node, code, features)
        elif language == 'php':
            self._extract_php_features(tree.root_node, code, features)
        else:
            self._extract_generic_features(tree.root_node, code, features)
        
        features.strings = list(set(s.strip('"\'') for s in features.strings if len(s.strip('"\'')) > 2))
        features.function_names = list(set(features.function_names))
        features.variable_names = list(set(features.variable_names))
        features.comments = list(set(c.strip() for c in features.comments if len(c.strip()) > 5))
        features.docstrings = list(set(d.strip() for d in features.docstrings if len(d.strip()) > 10))
        features.class_names = list(set(features.class_names))
        features.method_names = list(set(features.method_names))
        features.imports = list(set(features.imports))
        
        return features
    
    def _extract_python_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Python-specific features."""
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode(
                "utf8")
            print(node_text, node_type,end=' | \n')
            if node_type == 'string':
                features.strings.append(node_text)
                
                # Totally overcomplicated docstring detection
                parent = node.parent
                if (parent and parent.type == 'expression_statement' and
                    parent.parent and parent.parent.type in ['block', 'suite']):
                    
                    # Get the parent block and its parent (function/class)
                    block = parent.parent
                    definition = block.parent
                    
                    if (definition and definition.type in ['function_definition', 'class_definition'] and
                        block.children and parent == next((child for child in block.children 
                                                         if child.type not in ['newline', 'indent', 'dedent', ':']), None)):
                        
                        # This is a docstring - extract clean content
                        docstring_content = node_text.strip()
                        for quote in ['"""', "'''", '"', "'"]:
                            if docstring_content.startswith(quote) and docstring_content.endswith(quote):
                                docstring_content = docstring_content[len(quote):-len(quote)]
                                break
                        
                        features.docstrings.append(docstring_content.strip())
            
            # Function names
            elif node_type == "function_definition":
                func_name_node = node.child_by_field_name("name")
                if func_name_node:
                    features.function_names.append(
                        code_bytes[func_name_node.start_byte:func_name_node.end_byte].decode(
                            "utf8")
                    )

            # Class names
            elif node_type == "class_definition":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    features.class_names.append(
                        code_bytes[class_name_node.start_byte:class_name_node.end_byte].decode(
                            "utf8")
                    )

            # Variable names in assignments
            elif node_type == "assignment":
                target = node.child_by_field_name("left")
                if target and target.type == "identifier":
                    features.variable_names.append(
                        code_bytes[target.start_byte:target.end_byte].decode(
                            "utf8")
                    )

            # Imports
            elif node_type in ("import_statement", "import_from_statement"):
                features.imports.append(node_text)

            # Comments
            elif node_type == "comment":
                features.comments.append(node_text)
                    
            # Recursively process children
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_js_ts_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract JavaScript/TypeScript features."""
        def traverse(node: Node):
            node_type = node.type
            node_text = code[node.start_byte:node.end_byte]
            
            if node_type == 'string' or node_type == 'template_string':
                features.strings.append(node_text)
            
            elif node_type == 'function_declaration' or node_type == 'function_expression':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.function_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'arrow_function':
                # Arrow functions might not have explicit names
                pass
            
            elif node_type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'method_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.method_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'variable_declarator':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.variable_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'import_statement':
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_java_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Java features."""
        def traverse(node: Node):
            node_type = node.type
            node_text = code[node.start_byte:node.end_byte]
            
            if node_type == 'string_literal':
                features.strings.append(node_text)
            
            elif node_type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.method_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'variable_declarator':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.variable_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'import_declaration':
                features.imports.append(node_text)
            
            elif node_type == 'line_comment' or node_type == 'block_comment':
                features.comments.append(node_text)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_c_cpp_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract C/C++ features."""
        def traverse(node: Node):
            node_type = node.type
            node_text = code[node.start_byte:node.end_byte]
            
            if node_type == 'string_literal':
                features.strings.append(node_text)
            
            elif node_type == 'function_definition':
                declarator = node.child_by_field_name('declarator')
                if declarator and declarator.type == 'function_declarator':
                    name_node = declarator.child_by_field_name('declarator')
                    if name_node:
                        features.function_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'class_specifier':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'declaration':
                # Extract variable names from declarations
                for child in node.children:
                    if child.type == 'init_declarator':
                        declarator = child.child_by_field_name('declarator')
                        if declarator and declarator.type == 'identifier':
                            features.variable_names.append(code[declarator.start_byte:declarator.end_byte])
            
            elif node_type == 'preproc_include':
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_go_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Go features."""
        def traverse(node: Node):
            node_type = node.type
            node_text = code[node.start_byte:node.end_byte]
            
            if node_type == 'interpreted_string_literal' or node_type == 'raw_string_literal':
                features.strings.append(node_text)
            
            elif node_type == 'function_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.function_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'type_declaration':
                # For struct/interface declarations
                for child in node.children:
                    if child.type == 'type_spec':
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            features.class_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'var_declaration' or node_type == 'short_var_declaration':
                # Extract variable names
                for child in node.children:
                    if child.type == 'var_spec':
                        for grandchild in child.children:
                            if grandchild.type == 'identifier':
                                features.variable_names.append(code[grandchild.start_byte:grandchild.end_byte])
                                break
            
            elif node_type == 'import_declaration':
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_rust_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Rust features."""
        def traverse(node: Node):
            node_type = node.type
            node_text = code[node.start_byte:node.end_byte]
            
            if node_type == 'string_literal':
                features.strings.append(node_text)
            
            elif node_type == 'function_item':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.function_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'struct_item' or node_type == 'enum_item':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'let_declaration':
                pattern = node.child_by_field_name('pattern')
                if pattern and pattern.type == 'identifier':
                    features.variable_names.append(code[pattern.start_byte:pattern.end_byte])
            
            elif node_type == 'use_declaration':
                features.imports.append(node_text)
            
            elif node_type == 'line_comment' or node_type == 'block_comment':
                features.comments.append(node_text)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_ruby_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Ruby features.""" 
        def traverse(node: Node):
            node_type = node.type
            node_text = code[node.start_byte:node.end_byte]
            
            if node_type == 'string':
                features.strings.append(node_text)
            
            elif node_type == 'method':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.method_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'class':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'assignment':
                left = node.child_by_field_name('left')
                if left and left.type == 'identifier':
                    features.variable_names.append(code[left.start_byte:left.end_byte])
            
            elif node_type == 'require' or node_type == 'load':
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_php_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract PHP features."""
        def traverse(node: Node):
            node_type = node.type
            node_text = code[node.start_byte:node.end_byte]
            
            if node_type == 'string':
                features.strings.append(node_text)
            
            elif node_type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.function_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(code[name_node.start_byte:name_node.end_byte])
            
            elif node_type == 'assignment_expression':
                left = node.child_by_field_name('left')
                if left and left.type == 'variable_name':
                    features.variable_names.append(code[left.start_byte:left.end_byte])
            
            elif node_type == 'include_expression' or node_type == 'require_expression':
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_generic_features(self, node: Node, code: str, features: CodeFeatures):
        """Generic feature extraction for unsupported languages."""
        def traverse(node: Node):
            node_type = node.type
            node_text = code[node.start_byte:node.end_byte]
            
            # Extract strings
            if 'string' in node_type:
                features.strings.append(node_text)
            
            # Extract comments
            elif 'comment' in node_type:
                features.comments.append(node_text)
            
            # Extract identifiers as potential variable/function names
            elif node_type == 'identifier' and len(node_text) > 1:
                # Basic heuristic: longer identifiers are more likely to be meaningful
                if len(node_text) > 3:
                    features.variable_names.append(node_text)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _is_docstring(self, node: Node) -> bool:
        """Check if a string node is a docstring."""
        # Simple heuristic: check if parent is a function/class body and this is the first statement
        parent = node.parent
        if not parent:
            return False
        
        # Check if it's the first statement in a function/class body
        if parent.type in ['block', 'suite']:
            grandparent = parent.parent
            if grandparent and grandparent.type in ['function_definition', 'class_definition']:
                # Check if this string is the first non-whitespace statement
                for child in parent.children:
                    if child.type not in ['newline', 'indent', 'dedent']:
                        return child == node or (child.type == 'expression_statement' and node in child.children)
        
        return False
    
    def _fallback_extraction(self, code: str, language: str, file_path: Optional[str]) -> CodeFeatures:
        """Fallback regex-based extraction when Tree-sitter is not available."""
        features = CodeFeatures(
            strings=[],
            function_names=[],
            variable_names=[],
            comments=[],
            docstrings=[],
            class_names=[],
            method_names=[],
            imports=[],
            language=language,
            file_path=file_path
        )
        
        # Extract strings
        string_patterns = [
            r'"([^"\\]|\\.)*"',  # Double quoted
            r"'([^'\\]|\\.)*'",  # Single quoted
            r'`([^`\\]|\\.)*`'   # Backticks
        ]
        for pattern in string_patterns:
            features.strings.extend(re.findall(pattern, code))
        
        # Extract comments
        if language == 'python':
            features.comments.extend(re.findall(r'#.*', code))
            features.docstrings.extend(re.findall(r'"""(.*?)"""', code, re.DOTALL))
            features.docstrings.extend(re.findall(r"'''(.*?)'''", code, re.DOTALL))
        elif language in ['javascript', 'typescript', 'tsx', 'java', 'c', 'cpp', 'go', 'rust', 'php']:
            features.comments.extend(re.findall(r'//.*', code))
            features.comments.extend(re.findall(r'/\*(.*?)\*/', code, re.DOTALL))
        
        # Extract function/method names (basic patterns)
        if language == 'python':
            features.function_names.extend(re.findall(r'def\s+(\w+)', code))
            features.class_names.extend(re.findall(r'class\s+(\w+)', code))
        elif language in ['javascript', 'typescript', 'tsx']:
            features.function_names.extend(re.findall(r'function\s+(\w+)', code))
            features.class_names.extend(re.findall(r'class\s+(\w+)', code))
        elif language == 'java':
            features.method_names.extend(re.findall(r'(public|private|protected)?\s*(static)?\s*\w+\s+(\w+)\s*\(', code))
            features.class_names.extend(re.findall(r'class\s+(\w+)', code))
        
        # Extract variable names (very basic)
        if language == 'python':
            features.variable_names.extend(re.findall(r'(\w+)\s*=', code))
        
        return features
    
    def extract_from_file(self, file_path: str) -> Optional[CodeFeatures]:
        """Extract features from a code file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            language = self.detect_language(file_path)
            if not language:
                return None
            
            return self.extract_features(code, language, file_path)
        
        except Exception as e:
            print(f"Error extracting from {file_path}: {e}")
            return None
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self.parsers.keys())


# Example usage and utility functions
def extract_code_features(code: str, language: str, file_path: Optional[str] = None) -> CodeFeatures:
    """Convenience function to extract code features."""
    extractor = TreeSitterExtractor()
    return extractor.extract_features(code, language, file_path)


def extract_features_from_file(file_path: str) -> Optional[CodeFeatures]:
    """Convenience function to extract features from a file."""
    extractor = TreeSitterExtractor()
    return extractor.extract_from_file(file_path)


def features_to_dict(features: CodeFeatures) -> Dict[str, Any]:
    """Convert CodeFeatures to dictionary for JSON serialization."""
    return {
        'strings': features.strings,
        'function_names': features.function_names,
        'variable_names': features.variable_names,
        'comments': features.comments,
        'docstrings': features.docstrings,
        'class_names': features.class_names,
        'method_names': features.method_names,
        'imports': features.imports,
        'language': features.language,
        'file_path': features.file_path,
        'total_features': {
            'strings_count': len(features.strings),
            'functions_count': len(features.function_names),
            'variables_count': len(features.variable_names),
            'comments_count': len(features.comments),
            'docstrings_count': len(features.docstrings),
            'classes_count': len(features.class_names),
            'methods_count': len(features.method_names),
            'imports_count': len(features.imports)
        }
    }
