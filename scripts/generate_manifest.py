#!/usr/bin/env python3
"""
Transfer Function Library - Manifest Generator

Generates manifest.json containing:
- Library version
- Generation timestamp
- Per-table metadata (name, path, sha256, size)
- Bundle hash for verification
"""

import json
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_version(project_root: Path) -> str:
    """Read version from VERSION file."""
    version_file = project_root / 'VERSION'
    if not version_file.exists():
        raise FileNotFoundError(f"VERSION file not found at {version_file}")
    return version_file.read_text().strip()


def collect_tables(tables_dir: Path) -> dict:
    """
    Collect all .tfunc files and organize by category.

    Returns dict of categories, each containing list of table info.
    """
    categories = {}

    for filepath in sorted(tables_dir.rglob('*.tfunc')):
        rel_path = filepath.relative_to(tables_dir)
        content = filepath.read_bytes()

        # Determine category from directory
        if rel_path.parent == Path('.'):
            category = 'Uncategorized'
        else:
            category = str(rel_path.parent)

        if category not in categories:
            categories[category] = {'tables': []}

        table_info = {
            'name': filepath.stem,
            'file': str(rel_path),
            'sha256': hashlib.sha256(content).hexdigest(),
            'size': len(content)
        }

        categories[category]['tables'].append(table_info)

    # Sort tables within each category
    for cat in categories.values():
        cat['tables'].sort(key=lambda t: t['name'])

    return categories


def calculate_bundle_hash(tables_dir: Path) -> str:
    """
    Calculate a deterministic hash of all table files.

    Uses sorted file paths to ensure consistent ordering.
    """
    hasher = hashlib.sha256()

    for filepath in sorted(tables_dir.rglob('*.tfunc')):
        rel_path = str(filepath.relative_to(tables_dir))
        content = filepath.read_bytes()

        # Include path in hash for uniqueness
        hasher.update(rel_path.encode('utf-8'))
        hasher.update(content)

    return hasher.hexdigest()


def generate_manifest(project_root: Path, tables_dir: Path) -> dict:
    """Generate the complete manifest."""
    version = read_version(project_root)
    categories = collect_tables(tables_dir)

    # Count total tables
    total_tables = sum(len(cat['tables']) for cat in categories.values())

    manifest = {
        'version': version,
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'table_size': 16384,  # Expected samples per table
        'format_version': 3,  # JUCE ValueTree V3 format
        'bundle_sha256': calculate_bundle_hash(tables_dir),
        'categories': categories,
        'total_tables': total_tables
    }

    return manifest


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate manifest.json for transfer function library')
    parser.add_argument('--project-root', type=Path, default=Path('.'),
                        help='Project root directory (default: current directory)')
    parser.add_argument('--tables-dir', type=Path, default=None,
                        help='Tables directory (default: project_root/tables)')
    parser.add_argument('--output', type=Path, default=None,
                        help='Output path for manifest.json (default: project_root/manifest.json)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print manifest without writing to file')

    args = parser.parse_args()

    project_root = args.project_root.resolve()
    tables_dir = args.tables_dir or (project_root / 'tables')
    output_path = args.output or (project_root / 'manifest.json')

    if not tables_dir.exists():
        print(f"Error: Tables directory not found: {tables_dir}")
        sys.exit(1)

    print(f"Project root: {project_root}")
    print(f"Tables dir: {tables_dir}")
    print()

    # Generate manifest
    manifest = generate_manifest(project_root, tables_dir)

    print(f"Version: {manifest['version']}")
    print(f"Total tables: {manifest['total_tables']}")
    print(f"Categories: {', '.join(manifest['categories'].keys())}")
    print(f"Bundle hash: {manifest['bundle_sha256'][:16]}...")
    print()

    if args.dry_run:
        print("Manifest content:")
        print(json.dumps(manifest, indent=2))
    else:
        # Write manifest
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest written to: {output_path}")

    sys.exit(0)


if __name__ == '__main__':
    main()
