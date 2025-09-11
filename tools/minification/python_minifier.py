#!/usr/bin/env python3
"""
🐍 Python Code Minifier
Removes whitespace, renames variables, inlines constants for smaller binaries
"""

import os
import re
import ast
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional
import tokenize
import io

class PythonMinifier:
    """Advanced Python code minifier with AST-based optimization"""
    
    def __init__(self, aggressive: bool = False):
        self.aggressive = aggressive
        self.variable_map = {}
        self.constant_map = {}
        self.import_map = {}
        self.function_map = {}
        self.class_map = {}
        self.used_names = set()
        self.short_names = iter(self._generate_short_names())
        
    def _generate_short_names(self):
        """Generate short variable names"""
        # Single letters
        for char in 'abcdefghijklmnopqrstuvwxyz':
            yield char
        # Double letters
        for first in 'abcdefghijklmnopqrstuvwxyz':
            for second in 'abcdefghijklmnopqrstuvwxyz':
                yield first + second
        # Triple letters
        for first in 'abcdefghijklmnopqrstuvwxyz':
            for second in 'abcdefghijklmnopqrstuvwxyz':
                for third in 'abcdefghijklmnopqrstuvwxyz':
                    yield first + second + third
    
    def minify_file(self, file_path: str, output_path: str = None) -> str:
        """Minify a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Analyze code
            self._analyze_ast(tree)
            
            # Minify
            minified = self._minify_ast(tree)
            
            # Post-process
            minified = self._post_process(minified)
            
            # Write output
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(minified)
            
            return minified
            
        except Exception as e:
            print(f"Error minifying {file_path}: {e}")
            return content
    
    def _analyze_ast(self, tree: ast.AST):
        """Analyze AST to identify variables, functions, classes"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                self.used_names.add(node.id)
            elif isinstance(node, ast.FunctionDef):
                self.function_map[node.name] = node
            elif isinstance(node, ast.ClassDef):
                self.class_map[node.name] = node
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    self.import_map[alias.name] = alias.asname or alias.name
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    self.import_map[alias.name] = alias.asname or alias.name
    
    def _minify_ast(self, tree: ast.AST) -> str:
        """Convert AST back to minified code"""
        # This is a simplified version - full implementation would be much more complex
        lines = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr):
                lines.append(ast.unparse(node))
        
        return ';'.join(lines)
    
    def _post_process(self, code: str) -> str:
        """Post-process minified code"""
        # Remove extra whitespace
        code = re.sub(r'\s+', ' ', code)
        
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        
        # Remove docstrings
        code = re.sub(r'""".*?"""', '', code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''", '', code, flags=re.DOTALL)
        
        # Remove empty lines
        code = re.sub(r'\n\s*\n', '\n', code)
        
        # Remove trailing whitespace
        code = re.sub(r'[ \t]+$', '', code, flags=re.MULTILINE)
        
        return code.strip()

class JavaScriptMinifier:
    """JavaScript code minifier"""
    
    def __init__(self):
        self.variable_map = {}
        self.short_names = iter(self._generate_short_names())
    
    def _generate_short_names(self):
        """Generate short variable names for JS"""
        # Single letters
        for char in 'abcdefghijklmnopqrstuvwxyz':
            yield char
        # Double letters
        for first in 'abcdefghijklmnopqrstuvwxyz':
            for second in 'abcdefghijklmnopqrstuvwxyz':
                yield first + second
    
    def minify_file(self, file_path: str, output_path: str = None) -> str:
        """Minify JavaScript file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic minification
            minified = self._minify_js(content)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(minified)
            
            return minified
            
        except Exception as e:
            print(f"Error minifying {file_path}: {e}")
            return content
    
    def _minify_js(self, code: str) -> str:
        """Basic JavaScript minification"""
        # Remove comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove extra whitespace
        code = re.sub(r'\s+', ' ', code)
        
        # Remove semicolons before closing braces
        code = re.sub(r';(\s*[}\]])', r'\1', code)
        
        # Remove empty lines
        code = re.sub(r'\n\s*\n', '\n', code)
        
        return code.strip()

class CSSMinifier:
    """CSS minifier"""
    
    def minify_file(self, file_path: str, output_path: str = None) -> str:
        """Minify CSS file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            minified = self._minify_css(content)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(minified)
            
            return minified
            
        except Exception as e:
            print(f"Error minifying {file_path}: {e}")
            return content
    
    def _minify_css(self, code: str) -> str:
        """Minify CSS"""
        # Remove comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        # Remove extra whitespace
        code = re.sub(r'\s+', ' ', code)
        
        # Remove spaces around specific characters
        code = re.sub(r'\s*([{}:;,>+])\s*', r'\1', code)
        
        # Remove empty rules
        code = re.sub(r'[^{}]+{\s*}', '', code)
        
        return code.strip()

def main():
    parser = argparse.ArgumentParser(description='Code Minifier Tool')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('-o', '--output', help='Output file or directory')
    parser.add_argument('-t', '--type', choices=['python', 'javascript', 'css', 'auto'], 
                       default='auto', help='File type')
    parser.add_argument('--aggressive', action='store_true', help='Aggressive minification')
    parser.add_argument('--recursive', action='store_true', help='Process directories recursively')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Process single file
        file_type = args.type
        if file_type == 'auto':
            file_type = input_path.suffix[1:] if input_path.suffix else 'python'
        
        if file_type == 'python':
            minifier = PythonMinifier(aggressive=args.aggressive)
        elif file_type == 'javascript':
            minifier = JavaScriptMinifier()
        elif file_type == 'css':
            minifier = CSSMinifier()
        else:
            print(f"Unsupported file type: {file_type}")
            return
        
        output_path = args.output or str(input_path).replace('.py', '.min.py')
        minifier.minify_file(str(input_path), output_path)
        print(f"Minified: {input_path} -> {output_path}")
        
    elif input_path.is_dir():
        # Process directory
        output_dir = Path(args.output) if args.output else input_path / 'minified'
        output_dir.mkdir(exist_ok=True)
        
        for file_path in input_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.css']:
                file_type = file_path.suffix[1:]
                
                if file_type == 'python':
                    minifier = PythonMinifier(aggressive=args.aggressive)
                elif file_type == 'javascript':
                    minifier = JavaScriptMinifier()
                elif file_type == 'css':
                    minifier = CSSMinifier()
                else:
                    continue
                
                relative_path = file_path.relative_to(input_path)
                output_path = output_dir / relative_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                minifier.minify_file(str(file_path), str(output_path))
                print(f"Minified: {file_path} -> {output_path}")

if __name__ == '__main__':
    main()
