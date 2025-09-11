#!/usr/bin/env python3
"""
🚀 Workspace Optimizer
Comprehensive workspace analysis and optimization tool
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import hashlib
import mimetypes

class WorkspaceAnalyzer:
    """Comprehensive workspace analysis"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'workspace_path': str(self.workspace_path),
            'file_stats': {},
            'directory_stats': {},
            'duplicate_files': [],
            'large_files': [],
            'unused_files': [],
            'optimization_opportunities': [],
            'recommendations': []
        }
    
    def analyze_workspace(self) -> Dict:
        """Perform comprehensive workspace analysis"""
        print("🔍 Analyzing workspace...")
        
        # File and directory statistics
        self._analyze_file_stats()
        
        # Find duplicate files
        self._find_duplicates()
        
        # Find large files
        self._find_large_files()
        
        # Find unused files
        self._find_unused_files()
        
        # Analyze optimization opportunities
        self._analyze_optimization_opportunities()
        
        # Generate recommendations
        self._generate_recommendations()
        
        return self.analysis_results
    
    def _analyze_file_stats(self):
        """Analyze file and directory statistics"""
        print("📊 Analyzing file statistics...")
        
        file_types = {}
        total_size = 0
        file_count = 0
        directory_count = 0
        
        for root, dirs, files in os.walk(self.workspace_path):
            directory_count += len(dirs)
            
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        file_count += 1
                        
                        # Count by extension
                        ext = file_path.suffix.lower()
                        if ext not in file_types:
                            file_types[ext] = {'count': 0, 'size': 0}
                        file_types[ext]['count'] += 1
                        file_types[ext]['size'] += file_size
                        
                    except (OSError, PermissionError):
                        continue
        
        self.analysis_results['file_stats'] = {
            'total_files': file_count,
            'total_directories': directory_count,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'file_types': file_types
        }
    
    def _find_duplicates(self):
        """Find duplicate files using content hashing"""
        print("🔍 Finding duplicate files...")
        
        file_hashes = {}
        duplicates = []
        
        for root, dirs, files in os.walk(self.workspace_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    try:
                        # Calculate file hash
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        
                        if file_hash in file_hashes:
                            duplicates.append({
                                'hash': file_hash,
                                'original': str(file_hashes[file_hash]),
                                'duplicate': str(file_path),
                                'size': file_path.stat().st_size
                            })
                        else:
                            file_hashes[file_hash] = file_path
                            
                    except (OSError, PermissionError):
                        continue
        
        self.analysis_results['duplicate_files'] = duplicates
    
    def _find_large_files(self, threshold_mb: int = 10):
        """Find large files above threshold"""
        print(f"📏 Finding files larger than {threshold_mb}MB...")
        
        threshold_bytes = threshold_mb * 1024 * 1024
        large_files = []
        
        for root, dirs, files in os.walk(self.workspace_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size
                        if file_size > threshold_bytes:
                            large_files.append({
                                'path': str(file_path),
                                'size_bytes': file_size,
                                'size_mb': file_size / (1024 * 1024),
                                'extension': file_path.suffix.lower()
                            })
                    except (OSError, PermissionError):
                        continue
        
        # Sort by size descending
        large_files.sort(key=lambda x: x['size_bytes'], reverse=True)
        self.analysis_results['large_files'] = large_files[:50]  # Top 50
    
    def _find_unused_files(self):
        """Find potentially unused files"""
        print("🗑️ Finding potentially unused files...")
        
        unused_patterns = [
            '*.tmp', '*.temp', '*.log', '*.cache', '*.bak', '*.backup',
            '*.old', '*.orig', '*.swp', '*.swo', '*~', '*.pyc', '__pycache__',
            'node_modules', '.git', '.vscode', '.idea', '*.min.js', '*.min.css'
        ]
        
        unused_files = []
        
        for root, dirs, files in os.walk(self.workspace_path):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.is_file():
                    # Check if file matches unused patterns
                    for pattern in unused_patterns:
                        if file_path.match(pattern):
                            try:
                                unused_files.append({
                                    'path': str(file_path),
                                    'size_bytes': file_path.stat().st_size,
                                    'size_mb': file_path.stat().st_size / (1024 * 1024),
                                    'last_modified': datetime.fromtimestamp(
                                        file_path.stat().st_mtime
                                    ).isoformat()
                                })
                                break
                            except (OSError, PermissionError):
                                continue
        
        self.analysis_results['unused_files'] = unused_files
    
    def _analyze_optimization_opportunities(self):
        """Analyze optimization opportunities"""
        print("⚡ Analyzing optimization opportunities...")
        
        opportunities = []
        
        # Check for uncompressed assets
        asset_extensions = ['.css', '.js', '.html', '.json', '.xml', '.svg']
        uncompressed_assets = []
        
        for root, dirs, files in os.walk(self.workspace_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in asset_extensions:
                    # Check if compressed version exists
                    compressed_paths = [
                        file_path.with_suffix(file_path.suffix + '.gz'),
                        file_path.with_suffix(file_path.suffix + '.br')
                    ]
                    
                    if not any(p.exists() for p in compressed_paths):
                        uncompressed_assets.append(str(file_path))
        
        if uncompressed_assets:
            opportunities.append({
                'type': 'compression',
                'description': 'Uncompressed assets found',
                'files': uncompressed_assets[:10],  # Show first 10
                'total_count': len(uncompressed_assets),
                'estimated_savings': '20-70%'
            })
        
        # Check for unminified assets
        unminified_assets = []
        for root, dirs, files in os.walk(self.workspace_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ['.css', '.js']:
                    if 'min' not in file_path.name.lower():
                        unminified_assets.append(str(file_path))
        
        if unminified_assets:
            opportunities.append({
                'type': 'minification',
                'description': 'Unminified assets found',
                'files': unminified_assets[:10],
                'total_count': len(unminified_assets),
                'estimated_savings': '10-30%'
            })
        
        # Check for large images without optimization
        large_images = []
        for root, dirs, files in os.walk(self.workspace_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    try:
                        if file_path.stat().st_size > 500 * 1024:  # 500KB
                            large_images.append({
                                'path': str(file_path),
                                'size_mb': file_path.stat().st_size / (1024 * 1024)
                            })
                    except (OSError, PermissionError):
                        continue
        
        if large_images:
            opportunities.append({
                'type': 'image_optimization',
                'description': 'Large unoptimized images found',
                'files': large_images[:10],
                'total_count': len(large_images),
                'estimated_savings': '30-80%'
            })
        
        self.analysis_results['optimization_opportunities'] = opportunities
    
    def _generate_recommendations(self):
        """Generate optimization recommendations"""
        print("💡 Generating recommendations...")
        
        recommendations = []
        
        # File size recommendations
        total_size = self.analysis_results['file_stats']['total_size_mb']
        if total_size > 1000:  # 1GB
            recommendations.append({
                'priority': 'high',
                'category': 'storage',
                'title': 'Large workspace size',
                'description': f'Workspace is {total_size:.1f}MB. Consider cleanup.',
                'action': 'Run cleanup tools and archive old files'
            })
        
        # Duplicate files
        duplicates = len(self.analysis_results['duplicate_files'])
        if duplicates > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'duplicates',
                'title': 'Duplicate files found',
                'description': f'Found {duplicates} duplicate files.',
                'action': 'Remove duplicate files to save space'
            })
        
        # Large files
        large_files = len(self.analysis_results['large_files'])
        if large_files > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'large_files',
                'title': 'Large files found',
                'description': f'Found {large_files} files larger than 10MB.',
                'action': 'Review and optimize large files'
            })
        
        # Unused files
        unused_files = len(self.analysis_results['unused_files'])
        if unused_files > 0:
            recommendations.append({
                'priority': 'low',
                'category': 'cleanup',
                'title': 'Potentially unused files',
                'description': f'Found {unused_files} potentially unused files.',
                'action': 'Review and remove unused files'
            })
        
        # Optimization opportunities
        for opp in self.analysis_results['optimization_opportunities']:
            recommendations.append({
                'priority': 'medium' if opp['type'] in ['compression', 'minification'] else 'low',
                'category': opp['type'],
                'title': f'{opp["type"].title()} opportunity',
                'description': opp['description'],
                'action': f'Apply {opp["type"]} optimization (estimated savings: {opp["estimated_savings"]})'
            })
        
        self.analysis_results['recommendations'] = recommendations

class WorkspaceOptimizer:
    """Workspace optimization executor"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.tools_dir = Path(__file__).parent.parent
        
    def optimize_workspace(self, options: Dict = None) -> Dict:
        """Execute workspace optimization"""
        if not options:
            options = {
                'compress_assets': True,
                'minify_code': True,
                'remove_duplicates': False,
                'cleanup_temp_files': True,
                'optimize_images': False
            }
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'workspace_path': str(self.workspace_path),
            'optimizations_applied': [],
            'files_processed': 0,
            'space_saved': 0,
            'errors': []
        }
        
        # Compress assets
        if options.get('compress_assets'):
            try:
                compression_results = self._compress_assets()
                results['optimizations_applied'].append('asset_compression')
                results['files_processed'] += compression_results.get('files_processed', 0)
                results['space_saved'] += compression_results.get('space_saved', 0)
            except Exception as e:
                results['errors'].append(f'Asset compression failed: {e}')
        
        # Minify code
        if options.get('minify_code'):
            try:
                minification_results = self._minify_code()
                results['optimizations_applied'].append('code_minification')
                results['files_processed'] += minification_results.get('files_processed', 0)
                results['space_saved'] += minification_results.get('space_saved', 0)
            except Exception as e:
                results['errors'].append(f'Code minification failed: {e}')
        
        # Cleanup temp files
        if options.get('cleanup_temp_files'):
            try:
                cleanup_results = self._cleanup_temp_files()
                results['optimizations_applied'].append('temp_cleanup')
                results['files_processed'] += cleanup_results.get('files_processed', 0)
                results['space_saved'] += cleanup_results.get('space_saved', 0)
            except Exception as e:
                results['errors'].append(f'Temp cleanup failed: {e}')
        
        return results
    
    def _compress_assets(self) -> Dict:
        """Compress web assets"""
        compression_script = self.tools_dir / 'compression' / 'compression_manager.py'
        
        if not compression_script.exists():
            raise FileNotFoundError("Compression manager not found")
        
        # Find asset directories
        asset_dirs = []
        for pattern in ['**/static/**', '**/assets/**', '**/public/**', '**/dist/**']:
            asset_dirs.extend(self.workspace_path.glob(pattern))
        
        results = {'files_processed': 0, 'space_saved': 0}
        
        for asset_dir in asset_dirs:
            if asset_dir.is_dir():
                try:
                    cmd = [
                        sys.executable, str(compression_script),
                        str(asset_dir), '--optimize', '--recursive'
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    results['files_processed'] += len(list(asset_dir.rglob('*.css'))) + len(list(asset_dir.rglob('*.js')))
                except subprocess.CalledProcessError as e:
                    print(f"Error compressing {asset_dir}: {e}")
        
        return results
    
    def _minify_code(self) -> Dict:
        """Minify code files"""
        minifier_script = self.tools_dir / 'minification' / 'python_minifier.py'
        
        if not minifier_script.exists():
            raise FileNotFoundError("Minifier not found")
        
        results = {'files_processed': 0, 'space_saved': 0}
        
        # Find code directories
        code_dirs = []
        for pattern in ['**/src/**', '**/js/**', '**/css/**', 'NEXUS_app/**']:
            code_dirs.extend(self.workspace_path.glob(pattern))
        
        for code_dir in code_dirs:
            if code_dir.is_dir():
                try:
                    cmd = [
                        sys.executable, str(minifier_script),
                        str(code_dir), '--recursive'
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    results['files_processed'] += len(list(code_dir.rglob('*.py'))) + len(list(code_dir.rglob('*.js')))
                except subprocess.CalledProcessError as e:
                    print(f"Error minifying {code_dir}: {e}")
        
        return results
    
    def _cleanup_temp_files(self) -> Dict:
        """Cleanup temporary files"""
        temp_patterns = [
            '**/*.tmp', '**/*.temp', '**/*.log', '**/*.cache', '**/*.bak',
            '**/__pycache__/**', '**/*.pyc', '**/.DS_Store'
        ]
        
        files_processed = 0
        space_saved = 0
        
        for pattern in temp_patterns:
            for file_path in self.workspace_path.glob(pattern):
                if file_path.is_file():
                    try:
                        space_saved += file_path.stat().st_size
                        file_path.unlink()
                        files_processed += 1
                    except (OSError, PermissionError):
                        continue
                elif file_path.is_dir() and file_path.name == '__pycache__':
                    try:
                        shutil.rmtree(file_path)
                        files_processed += 1
                    except (OSError, PermissionError):
                        continue
        
        return {
            'files_processed': files_processed,
            'space_saved': space_saved
        }

def main():
    parser = argparse.ArgumentParser(description='Workspace Optimizer')
    parser.add_argument('workspace', help='Workspace path to analyze/optimize')
    parser.add_argument('--analyze', action='store_true', help='Analyze workspace only')
    parser.add_argument('--optimize', action='store_true', help='Optimize workspace')
    parser.add_argument('--output', help='Output file for analysis results')
    parser.add_argument('--compress-assets', action='store_true', help='Compress assets')
    parser.add_argument('--minify-code', action='store_true', help='Minify code')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup temp files')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyzer = WorkspaceAnalyzer(args.workspace)
        results = analyzer.analyze_workspace()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 WORKSPACE ANALYSIS SUMMARY")
        print("="*60)
        
        stats = results['file_stats']
        print(f"📁 Total files: {stats['total_files']:,}")
        print(f"📂 Total directories: {stats['total_directories']:,}")
        print(f"💾 Total size: {stats['total_size_mb']:.1f} MB")
        
        print(f"\n🔍 Duplicate files: {len(results['duplicate_files'])}")
        print(f"📏 Large files (>10MB): {len(results['large_files'])}")
        print(f"🗑️ Unused files: {len(results['unused_files'])}")
        print(f"⚡ Optimization opportunities: {len(results['optimization_opportunities'])}")
        
        print(f"\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"  [{rec['priority'].upper()}] {rec['title']}: {rec['action']}")
        
        # Save results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Results saved to: {args.output}")
    
    if args.optimize:
        optimizer = WorkspaceOptimizer(args.workspace)
        options = {
            'compress_assets': args.compress_assets,
            'minify_code': args.minify_code,
            'cleanup_temp_files': args.cleanup
        }
        
        results = optimizer.optimize_workspace(options)
        
        print("\n" + "="*60)
        print("🚀 OPTIMIZATION RESULTS")
        print("="*60)
        
        print(f"📁 Files processed: {results['files_processed']}")
        print(f"💾 Space saved: {results['space_saved'] / (1024*1024):.1f} MB")
        print(f"⚡ Optimizations applied: {', '.join(results['optimizations_applied'])}")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors']:
                print(f"  {error}")

if __name__ == '__main__':
    main()
