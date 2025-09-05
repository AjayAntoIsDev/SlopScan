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
    
    def __init__(self):
        self.parsers = {}
        self.languages = {}
        self._init_languages()
    
    def _init_languages(self):
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
                    print(f"Warning: Could not find language function in {module_name}")
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
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
            if node_type == 'string':
                features.strings.append(node_text)
                
                # Totally overcomplicated docstring detection
                parent = node.parent
                if (parent and parent.type == 'expression_statement' and
                    parent.parent and parent.parent.type in ['block', 'suite']):
                    
                    block = parent.parent
                    definition = block.parent
                    
                    if (definition and definition.type in ['function_definition', 'class_definition'] and
                        block.children and parent == next((child for child in block.children 
                                                         if child.type not in ['newline', 'indent', 'dedent', ':']), None)):
                        
                        docstring_content = node_text.strip()
                        for quote in ['"""', "'''", '"', "'"]:
                            if docstring_content.startswith(quote) and docstring_content.endswith(quote):
                                docstring_content = docstring_content[len(quote):-len(quote)]
                                break
                        
                        features.docstrings.append(docstring_content.strip())
            
            elif node_type == "function_definition":
                func_name_node = node.child_by_field_name("name")
                if func_name_node:
                    features.function_names.append(
                        code_bytes[func_name_node.start_byte:func_name_node.end_byte].decode("utf8")
                    )

            elif node_type == "class_definition":
                class_name_node = node.child_by_field_name("name")
                if class_name_node:
                    features.class_names.append(
                        code_bytes[class_name_node.start_byte:class_name_node.end_byte].decode("utf8")
                    )

            elif node_type == "assignment":
                target = node.child_by_field_name("left")
                if target and target.type == "identifier":
                    features.variable_names.append(
                        code_bytes[target.start_byte:target.end_byte].decode("utf8")
                    )

            elif node_type in ("import_statement", "import_from_statement"):
                features.imports.append(node_text)

            elif node_type == "comment":
                features.comments.append(node_text)
                    
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_js_ts_features(self, node: Node, code: str, features: CodeFeatures):
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
            if node_type == 'string' or node_type == 'template_string':
                features.strings.append(node_text)
                
                parent = node.parent
                if (parent and parent.type == 'comment' and 
                    node_text.strip().startswith('/**') and node_text.strip().endswith('*/')):
                    
                    docstring_content = node_text.strip()
                    if docstring_content.startswith('/**') and docstring_content.endswith('*/'):
                        docstring_content = docstring_content[3:-2].strip()
                        features.docstrings.append(docstring_content)
            
            elif node_type == 'function_declaration' or node_type == 'function_expression':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.function_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'arrow_function':
                parent = node.parent
                if parent and parent.type == 'variable_declarator':
                    name_node = parent.child_by_field_name('name')
                    if name_node:
                        features.function_names.append(
                            code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                        )
            
            elif node_type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'method_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.method_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'variable_declarator':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.variable_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type in ('import_statement', 'import_declaration'):
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
                
                if node_text.strip().startswith('/**') and node_text.strip().endswith('*/'):
                    docstring_content = node_text.strip()[3:-2].strip()
                    if len(docstring_content) > 10:
                        features.docstrings.append(docstring_content)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_java_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Java features."""
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
            if node_type == 'string_literal':
                features.strings.append(node_text)
            
            elif node_type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.method_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'class_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'variable_declarator':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.variable_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'import_declaration':
                features.imports.append(node_text)
            
            elif node_type in ('line_comment', 'block_comment'):
                features.comments.append(node_text)
                
                if node_type == 'block_comment' and node_text.strip().startswith('/**'):
                    docstring_content = node_text.strip()
                    if docstring_content.startswith('/**') and docstring_content.endswith('*/'):
                        docstring_content = docstring_content[3:-2].strip()
                        if len(docstring_content) > 10:
                            features.docstrings.append(docstring_content)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_c_cpp_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract C/C++ features."""
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
            if node_type == 'string_literal':
                features.strings.append(node_text)
            
            elif node_type == 'function_definition':
                declarator = node.child_by_field_name('declarator')
                if declarator and declarator.type == 'function_declarator':
                    name_node = declarator.child_by_field_name('declarator')
                    if name_node:
                        features.function_names.append(
                            code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                        )
            
            elif node_type in ('class_specifier', 'struct_specifier'):
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'declaration':
                for child in node.children:
                    if child.type == 'init_declarator':
                        declarator = child.child_by_field_name('declarator')
                        if declarator and declarator.type == 'identifier':
                            features.variable_names.append(
                                code_bytes[declarator.start_byte:declarator.end_byte].decode("utf8")
                            )
            
            elif node_type in ('preproc_include', 'preproc_import'):
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
                
                # Check for Doxygen-style comments
                if (node_text.strip().startswith('/**') or 
                    node_text.strip().startswith('///') or
                    node_text.strip().startswith('/*!')):
                    
                    docstring_content = node_text.strip()
                    # Clean up different comment styles
                    for prefix, suffix in [('/**', '*/'), ('/*！', '*/'), ('///', ''), ('//!', '')]:
                        if docstring_content.startswith(prefix):
                            if suffix and docstring_content.endswith(suffix):
                                docstring_content = docstring_content[len(prefix):-len(suffix)]
                            else:
                                docstring_content = docstring_content[len(prefix):]
                            break
                    
                    docstring_content = docstring_content.strip()
                    if len(docstring_content) > 10:
                        features.docstrings.append(docstring_content)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_go_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Go features."""
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
            if node_type in ('interpreted_string_literal', 'raw_string_literal'):
                features.strings.append(node_text)
            
            elif node_type == 'function_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.function_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.method_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'type_declaration':
                for child in node.children:
                    if child.type == 'type_spec':
                        name_node = child.child_by_field_name('name')
                        if name_node:
                            features.class_names.append(
                                code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                            )
            
            elif node_type in ('var_declaration', 'short_var_declaration', 'const_declaration'):
                for child in node.children:
                    if child.type == 'var_spec' or child.type == 'const_spec':
                        for grandchild in child.children:
                            if grandchild.type == 'identifier':
                                features.variable_names.append(
                                    code_bytes[grandchild.start_byte:grandchild.end_byte].decode("utf8")
                                )
                                break
                    elif child.type == 'expression_list':
                        for expr in child.children:
                            if expr.type == 'identifier':
                                features.variable_names.append(
                                    code_bytes[expr.start_byte:expr.end_byte].decode("utf8")
                                )
            
            elif node_type == 'import_declaration':
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
                
                if node_text.strip().startswith('//'):
                    next_sibling = node.next_sibling
                    if (next_sibling and 
                        next_sibling.type in ['function_declaration', 'type_declaration', 'method_declaration']):
                        
                        docstring_content = node_text.strip()
                        if docstring_content.startswith('//'):
                            docstring_content = docstring_content[2:].strip()
                            if len(docstring_content) > 10:
                                features.docstrings.append(docstring_content)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_rust_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Rust features."""
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
            if node_type == 'string_literal':
                features.strings.append(node_text)
            
            elif node_type == 'function_item':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.function_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type in ('struct_item', 'enum_item', 'trait_item', 'impl_item'):
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'let_declaration':
                pattern = node.child_by_field_name('pattern')
                if pattern and pattern.type == 'identifier':
                    features.variable_names.append(
                        code_bytes[pattern.start_byte:pattern.end_byte].decode("utf8")
                    )
            
            elif node_type in ('use_declaration', 'extern_crate_declaration'):
                features.imports.append(node_text)
            
            elif node_type in ('line_comment', 'block_comment'):
                features.comments.append(node_text)
                
                # Check for Rust doc comments
                if (node_text.strip().startswith('///') or 
                    node_text.strip().startswith('//!') or
                    node_text.strip().startswith('/**') or
                    node_text.strip().startswith('/*!')):
                    
                    docstring_content = node_text.strip()
                    for prefix, suffix in [('///', ''), ('//!', ''), ('/**', '*/'), ('/*!', '*/')]:
                        if docstring_content.startswith(prefix):
                            if suffix and docstring_content.endswith(suffix):
                                docstring_content = docstring_content[len(prefix):-len(suffix)]
                            else:
                                docstring_content = docstring_content[len(prefix):]
                            break
                    
                    docstring_content = docstring_content.strip()
                    if len(docstring_content) > 10:
                        features.docstrings.append(docstring_content)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_ruby_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract Ruby features.""" 
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
            if node_type == 'string':
                features.strings.append(node_text)
            
            elif node_type == 'method':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.method_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'class':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'module':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'assignment':
                left = node.child_by_field_name('left')
                if left and left.type == 'identifier':
                    features.variable_names.append(
                        code_bytes[left.start_byte:left.end_byte].decode("utf8")
                    )
            
            elif node_type in ('require', 'load', 'require_relative'):
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
                
                # Check for YARD documentation comments (starting with ##)
                if node_text.strip().startswith('#'):
                    # Look for method/class documentation (comments directly before declarations)
                    next_sibling = node.next_sibling
                    if (next_sibling and 
                        next_sibling.type in ['method', 'class', 'module']):
                        
                        docstring_content = node_text.strip()
                        if docstring_content.startswith('#'):
                            docstring_content = docstring_content[1:].strip()
                            if len(docstring_content) > 10:
                                features.docstrings.append(docstring_content)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_php_features(self, node: Node, code: str, features: CodeFeatures):
        """Extract PHP features."""
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
            if node_type == 'string':
                features.strings.append(node_text)
            
            elif node_type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.function_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'method_declaration':
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.method_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type in ('class_declaration', 'interface_declaration', 'trait_declaration'):
                name_node = node.child_by_field_name('name')
                if name_node:
                    features.class_names.append(
                        code_bytes[name_node.start_byte:name_node.end_byte].decode("utf8")
                    )
            
            elif node_type == 'assignment_expression':
                left = node.child_by_field_name('left')
                if left and left.type == 'variable_name':
                    features.variable_names.append(
                        code_bytes[left.start_byte:left.end_byte].decode("utf8")
                    )
            
            elif node_type in ('include_expression', 'require_expression', 'include_once_expression', 'require_once_expression'):
                features.imports.append(node_text)
            
            elif node_type == 'comment':
                features.comments.append(node_text)
                
                # Check for PHPDoc comments
                if (node_text.strip().startswith('/**') or 
                    node_text.strip().startswith('/*')):
                    
                    docstring_content = node_text.strip()
                    if docstring_content.startswith('/**') and docstring_content.endswith('*/'):
                        docstring_content = docstring_content[3:-2].strip()
                        if len(docstring_content) > 10:
                            features.docstrings.append(docstring_content)
                    elif docstring_content.startswith('/*') and docstring_content.endswith('*/'):
                        # Check if it looks like documentation
                        content = docstring_content[2:-2].strip()
                        if any(marker in content for marker in ['@param', '@return', '@throws', '@var', '@author']):
                            features.docstrings.append(content)
            
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
    def _extract_generic_features(self, node: Node, code: str, features: CodeFeatures):
        """For unsupported languages."""
        def traverse(node: Node):
            code_bytes = code.encode("utf8")
            node_type = node.type
            node_text = code_bytes[node.start_byte:node.end_byte].decode("utf8")
            
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
            
            # Recursively process children
            for child in node.children:
                traverse(child)
        
        traverse(node)
    
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
    
    def get_supported_languages(self) -> List[str]:
        return list(self.parsers.keys())



def features_to_dict(features: CodeFeatures) -> Dict[str, Any]:
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
    }
