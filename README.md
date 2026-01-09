# Transfer Function Library

Shared nonlinear transfer function tables for Aspen Instruments audio plugins.

## Overview

This library contains curated transfer function wavetables used across multiple
Aspen Instruments plugins. Each transfer function defines a nonlinear mapping
that shapes audio signals, providing various saturation, distortion, and
waveshaping characteristics.

## Structure

```
transfer-function-library/
├── tables/
│   ├── Basic Shapes/      # Fundamental waveforms (tanh, sine, etc.)
│   ├── Classic Hardware/  # Emulations of classic analog gear
│   ├── Experimental/      # Creative/unusual transfer functions
│   └── Trig Harmonics/    # Mathematically-derived harmonic content
├── scripts/
│   ├── validate_tables.py    # Validation script
│   └── generate_manifest.py  # Manifest generator
├── manifest.json          # Auto-generated bundle metadata
├── VERSION                # Semantic version
└── LICENSE.txt
```

## File Format

Transfer functions use the `.tfunc` format:
- JUCE ValueTree binary format (V3)
- zlib-compressed base layer data
- 16,384 double-precision samples per table
- Covers input range [-1, 1]

## Versioning

This library follows semantic versioning:

| Change Type | Version Bump |
|-------------|--------------|
| Metadata/docs only | PATCH |
| Add new tables | MINOR |
| Modify existing table | MAJOR |
| Remove/rename table | MAJOR |

## Integration

### For Plugin Developers

1. **Pin a version** in your plugin repo:
   ```
   # tfl.version
   1.0.0 <manifest-sha256>
   ```

2. **Fetch during build**:
   ```bash
   ./scripts/fetch_tfl.sh
   ```

3. **Tables are extracted to** `factory-presets/`

### For Contributors

1. Add new `.tfunc` files to the appropriate category in `tables/`
2. Run validation: `python scripts/validate_tables.py tables/`
3. Open a PR - CI will validate automatically
4. Upon merge to main, tag a release to publish artifacts

## Validation

```bash
# Validate all tables
python scripts/validate_tables.py tables/

# Check for duplicates
python scripts/validate_tables.py tables/ --check-determinism

# Generate manifest
python scripts/generate_manifest.py
```

## License

Copyright (c) 2025 Aspen Instruments LLC. All rights reserved.

See [LICENSE.txt](LICENSE.txt) for terms.
