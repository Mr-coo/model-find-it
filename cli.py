#!/usr/bin/env python
"""
Command-Line Interface for Unified Fruit Analysis Pipeline

Usage:
    python cli.py analyze <image_path>
    python cli.py batch <directory_path>
    python cli.py server
    python cli.py health
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from unified_pipeline import UnifiedFruitAnalyzer, FruitAnalysisService
import subprocess
import platform


class FruitAnalyzerCLI:
    """Command-line interface for the unified fruit analyzer"""
    
    def __init__(self):
        self.analyzer = None
        self.service = None
    
    def init_analyzer(self):
        """Initialize the analyzer"""
        if self.analyzer is None:
            print("🔄 Initializing analyzer...")
            try:
                self.analyzer = UnifiedFruitAnalyzer()
                print("✅ Analyzer ready!")
            except Exception as e:
                print(f"❌ Error initializing analyzer: {e}")
                sys.exit(1)
    
    def init_service(self):
        """Initialize the backend service"""
        if self.service is None:
            print("🔄 Initializing service...")
            try:
                self.service = FruitAnalysisService()
                print("✅ Service ready!")
            except Exception as e:
                print(f"❌ Error initializing service: {e}")
                sys.exit(1)
    
    def analyze_image(self, image_path: str, output: Optional[str] = None, visualize: bool = False):
        """Analyze a single image"""
        self.init_analyzer()
        
        image_file = Path(image_path)
        if not image_file.exists():
            print(f"❌ Image file not found: {image_path}")
            sys.exit(1)
        
        print(f"\n📸 Analyzing: {image_path}")
        print("-" * 60)
        
        result = self.analyzer.analyze(image_path, visualize=visualize)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            sys.exit(1)
        
        # Display results
        self._print_result(result)
        
        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n✅ Results saved to: {output}")
    
    def analyze_batch(self, directory: str, output: Optional[str] = None):
        """Analyze multiple images in a directory"""
        self.init_analyzer()
        
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"❌ Directory not found: {directory}")
            sys.exit(1)
        
        print(f"\n📁 Batch analyzing: {directory}")
        print("-" * 60)
        
        results = self.analyzer.analyze_batch(directory)
        
        if not results:
            print("❌ No images found in directory")
            sys.exit(1)
        
        print(f"\n✅ Analyzed {len(results)} images\n")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {Path(result['image_path']).name}")
            self._print_result(result)
        
        # Save results if requested
        if output:
            self.analyzer.save_results(results, output)
        
        return results
    
    def start_server(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Start the Flask backend server"""
        print("\n🚀 Starting Fruit Analysis Service...")
        print(f"📍 Server: http://{host}:{port}")
        print(f"\n📚 API Documentation: http://{host}:{port}/api/docs")
        print(f"🏥 Health Check: http://{host}:{port}/health")
        print("\nPress Ctrl+C to stop\n")
        
        try:
            from backend_service import app
            app.run(host=host, port=port, debug=debug)
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)
    
    def health_check(self):
        """Check service health"""
        self.init_service()
        
        print("\n🏥 Health Check")
        print("-" * 60)
        
        status = self.service.get_health_status()
        
        print(f"Status: {status.get('status', 'unknown').upper()}")
        print(f"Fruit Classifier: {'✅' if status.get('fruit_classifier') else '❌'}")
        print(f"Freshness Detector: {'✅' if status.get('freshness_detector') else '❌'}")
        print(f"Timestamp: {status.get('timestamp')}")
    
    def _print_result(self, result):
        """Pretty print analysis result"""
        
        # Classification
        if result.get('classification'):
            clf = result['classification']
            print(f"\n📍 CLASSIFICATION")
            print(f"   Type: {clf['fruit_type']}")
            print(f"   Confidence: {clf['confidence']:.1%}")
        
        # Freshness
        if result.get('freshness'):
            fresh = result['freshness']
            emoji = '✅' if fresh['status'] == 'fresh' else '❌'
            print(f"\n🍎 FRESHNESS: {emoji} {fresh['status'].upper()}")
            print(f"   Confidence: {fresh['confidence']:.1%}")
        
        # Dimensions
        if result.get('physical_dimensions'):
            dims = result['physical_dimensions']
            if dims['width']:
                print(f"\n📏 DIMENSIONS")
                print(f"   Width: {dims['width']:.2f} px")
                print(f"   Height: {dims['height']:.2f} px")
                if dims.get('area'):
                    print(f"   Area: {dims['area']:.2f} px²")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Unified Fruit Analysis Pipeline - CLI Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python cli.py analyze image.jpg
  python cli.py analyze image.jpg -o result.json
  python cli.py batch ./fruits_directory
  python cli.py batch ./fruits_directory -o results.json
  python cli.py server
  python cli.py server --port 8000
  python cli.py health
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single image')
    analyze_parser.add_argument('image', help='Path to image file')
    analyze_parser.add_argument('-o', '--output', help='Output JSON file path')
    analyze_parser.add_argument('-v', '--visualize', action='store_true', help='Display visualization')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Analyze multiple images')
    batch_parser.add_argument('directory', help='Directory containing images')
    batch_parser.add_argument('-o', '--output', help='Output JSON file path')
    
    # Server command
    server_parser = subparsers.add_parser('server', help='Start backend service')
    server_parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    server_parser.add_argument('--port', type=int, default=5000, help='Server port (default: 5000)')
    server_parser.add_argument('-d', '--debug', action='store_true', help='Enable debug mode')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Check service health')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = FruitAnalyzerCLI()
    
    if args.command == 'analyze':
        cli.analyze_image(args.image, output=args.output, visualize=args.visualize)
    
    elif args.command == 'batch':
        cli.analyze_batch(args.directory, output=args.output)
    
    elif args.command == 'server':
        cli.start_server(host=args.host, port=args.port, debug=args.debug)
    
    elif args.command == 'health':
        cli.health_check()


if __name__ == '__main__':
    main()
