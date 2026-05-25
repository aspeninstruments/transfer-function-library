# Changelog

All notable changes to the Transfer Function Library will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0-beta] - 2026-05-24

### Changed
- Renamed all 57 `Hardware Models/` transfer functions to obscured all-caps
  codes that drop trademarked brand names from titles (`Neve1073 A` ->
  `N1073-A`, `LA-2A-Tube A` -> `L2A-A`, `LA-6176 A` -> `L76-A`,
  `LA-6176-500Ohm A` -> `L76-500-A`, `LA-6176-Mic A` -> `L76-Mic-A`,
  `Distressor A` -> `DSTRESS-A`, `Distressor-1P A` -> `DSTRESS-1P-A`,
  `Fairchild 660/670` -> `FAIR660/FAIR670`, `Pultec` -> `PUL1A`,
  `Green Russian` -> `GMUFF`, `AC10 A` -> `VX10-A`, `Bassman A` -> `BMAN-A`,
  `Plasma Coil A` -> `PLAS-A`, `VT-737-Soft-Clip` -> `V737 SoftClip`,
  `Imperial A` / `TK Imperial` -> `TKIMP-A` / `TKIMP`). Full brand names are
  never spelled out in the title; the real brand + model is retained in the
  embedded `description` ("Transfer Function inspired by the ...") for
  in-plugin browser search.
- Stamped `artist = "Astrobear"` on every hardware capture for uniform
  credit in the in-plugin browser.
- Per-file metadata upgraded from format v3 to v4 (additive `description`
  field; v3 readers continue to load these files normally).
- Tagged each capture with brand and category short codes (Neve, UA,
  Empirical, Fender, Vox, Avalon, Tone King, Gamechanger, Sovtek, Fairchild,
  Pultec, JHS, plus Preamp/Compressor/Limiter/EQ/Amplifier/Pedal/Channel
  Strip/Fuzz).

## [1.0.0] - 2025-01-08

### Added
- Initial release with transfer functions from Black Diamond Distortion
- Basic Shapes category (Linear, Tanh variants, Sine variants, etc.)
- Classic Hardware category (tape, tube, transistor emulations)
- Experimental category (creative waveshaping algorithms)
- Trig Harmonics category (mathematically-derived functions)
- Validation script for .tfunc file integrity
- Manifest generator for bundle metadata
- CI workflows for validation and releases
