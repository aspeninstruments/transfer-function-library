#!/usr/bin/env python3
"""
Transfer Function Library - Table Validation Script

Validates .tfunc files for:
- Correct file structure (JUCE ValueTree binary format)
- Presence of required elements (Preset root, formatVersion, baseLayer)
- zlib compression markers
- Reasonable file sizes

For deep content validation (NaN/inf/bounds), use the C++ validation tool.
"""

import os
import sys
import hashlib
import struct
from pathlib import Path


# Expected constants
MIN_FILE_SIZE = 300        # Minimum valid .tfunc size (highly compressible data can be small)
MAX_FILE_SIZE = 500000     # Maximum expected size (uncompressed would be ~131KB)
EXPECTED_TABLE_SIZE = 16384
EXPECTED_FORMAT_VERSION = 3

# JUCE ValueTree binary format markers
PRESET_HEADER = b'Preset'
ZLIB_HEADER = b'\x78\xda'  # zlib compression level 9


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_file_structure(filepath: Path) -> dict:
    """
    Validate a .tfunc file structure.

    Returns dict with:
        - valid: bool
        - sha256: str (file hash)
        - size: int (file size in bytes)
        - error: str (if invalid)
    """
    result = {
        'valid': False,
        'sha256': '',
        'size': 0,
        'error': None
    }

    try:
        # Check file exists and is readable
        if not filepath.exists():
            raise ValidationError(f"File not found: {filepath}")

        if not filepath.is_file():
            raise ValidationError(f"Not a file: {filepath}")

        # Read file content
        content = filepath.read_bytes()
        result['size'] = len(content)

        # Calculate SHA256
        result['sha256'] = hashlib.sha256(content).hexdigest()

        # Check file size bounds
        if len(content) < MIN_FILE_SIZE:
            raise ValidationError(f"File too small: {len(content)} bytes (min: {MIN_FILE_SIZE})")

        if len(content) > MAX_FILE_SIZE:
            raise ValidationError(f"File too large: {len(content)} bytes (max: {MAX_FILE_SIZE})")

        # Check for Preset header (JUCE ValueTree root element)
        if not content.startswith(PRESET_HEADER):
            raise ValidationError(f"Missing 'Preset' header - not a valid .tfunc file")

        # Check for formatVersion marker
        if b'formatVersion' not in content:
            raise ValidationError("Missing 'formatVersion' property")

        # Check for transferFunction element
        if b'transferFunction' not in content:
            raise ValidationError("Missing 'transferFunction' element")

        # Check for baseLayer element
        if b'baseLayer' not in content:
            raise ValidationError("Missing 'baseLayer' element")

        # Check for zlib compression marker
        if b'compression' not in content or b'zlib' not in content:
            raise ValidationError("Missing zlib compression indicator")

        # Check for zlib header in data section
        if ZLIB_HEADER not in content:
            raise ValidationError("Missing zlib compressed data header (0x78da)")

        # Check for data property
        if b'data' not in content:
            raise ValidationError("Missing 'data' property in baseLayer")

        result['valid'] = True

    except ValidationError as e:
        result['error'] = str(e)
    except Exception as e:
        result['error'] = f"Unexpected error: {e}"

    return result


def validate_directory(tables_dir: Path) -> tuple[list, list]:
    """
    Validate all .tfunc files in a directory tree.

    Returns:
        (valid_files, errors)
        - valid_files: list of dicts with file info
        - errors: list of error messages
    """
    valid_files = []
    errors = []

    # Find all .tfunc files
    tfunc_files = sorted(tables_dir.rglob('*.tfunc'))

    if not tfunc_files:
        errors.append(f"No .tfunc files found in {tables_dir}")
        return valid_files, errors

    print(f"Found {len(tfunc_files)} .tfunc files")

    for filepath in tfunc_files:
        rel_path = filepath.relative_to(tables_dir)
        result = validate_file_structure(filepath)

        if result['valid']:
            valid_files.append({
                'path': str(rel_path),
                'name': filepath.stem,
                'category': str(rel_path.parent) if rel_path.parent != Path('.') else 'Uncategorized',
                'sha256': result['sha256'],
                'size': result['size']
            })
            print(f"  OK: {rel_path}")
        else:
            errors.append(f"{rel_path}: {result['error']}")
            print(f"  FAIL: {rel_path} - {result['error']}")

    return valid_files, errors


def check_determinism(tables_dir: Path) -> list:
    """
    Check for duplicate files (same content, different paths).
    This helps catch accidental duplicates.

    Returns list of warnings about potential duplicates.
    """
    warnings = []
    hash_to_files = {}

    for filepath in tables_dir.rglob('*.tfunc'):
        content = filepath.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        rel_path = str(filepath.relative_to(tables_dir))

        if file_hash in hash_to_files:
            warnings.append(f"Duplicate content: '{rel_path}' matches '{hash_to_files[file_hash]}'")
        else:
            hash_to_files[file_hash] = rel_path

    return warnings


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Validate transfer function table files')
    parser.add_argument('tables_dir', type=Path, help='Path to tables directory')
    parser.add_argument('--check-determinism', action='store_true',
                        help='Check for duplicate files')
    parser.add_argument('--strict', action='store_true',
                        help='Exit with error on any warning')

    args = parser.parse_args()

    if not args.tables_dir.exists():
        print(f"Error: Directory not found: {args.tables_dir}")
        sys.exit(1)

    print(f"Validating tables in: {args.tables_dir}")
    print()

    # Validate all files
    valid_files, errors = validate_directory(args.tables_dir)

    print()
    print(f"Results: {len(valid_files)} valid, {len(errors)} errors")

    # Check for duplicates if requested
    warnings = []
    if args.check_determinism:
        print()
        print("Checking for duplicates...")
        warnings = check_determinism(args.tables_dir)
        for w in warnings:
            print(f"  WARNING: {w}")

    # Summary
    print()
    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)
    elif warnings and args.strict:
        print("VALIDATION FAILED (strict mode)")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
