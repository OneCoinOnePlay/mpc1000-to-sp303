# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-01-18

### Added
- Initial release
- MPC1000 .pgm file parser
- SP-303 bank organizer (creates 8 banks from 64 pads)
- Sample preprocessing with automatic padding
- Support for all 64 MPC pads
- Automatic file renaming to SP-303 format (SMPL0001.WAV, etc.)

### Features
- Parses MPC1000 .pgm file structure (164-byte pad entries)
- Pads samples shorter than 110ms (hardware-tested minimum)
- Creates Bank_A through Bank_H folders
- Intelligent WAV file matching (exact, case-insensitive, partial)
- Format checking (44.1kHz, 16-bit)
- No external dependencies (Python standard library only)

### Testing
- Tested with MPC1000 VinylDrumsMars1.pgm
- Verified on actual Boss Dr. Sample SP-303 hardware
- Sample duration testing: 110ms minimum confirmed
- Various sample formats tested (mono/stereo, different durations)

### Documentation
- Complete README with quick start guide
- Detailed COMPLETE_README with technical specifications
- Bank mapping reference
- Troubleshooting guide
- Contributing guidelines

### Known Limitations
- Only supports MPC1000 .pgm format
- Basic format conversion (recommends ffmpeg for complex conversions)
- WAV files must match sample names in .pgm file

---

## Future Considerations

Potential features for future releases:
- Support for MPC500, MPC2500, MPC Live/X
- Support for SP-404, SP-555
- Automatic format conversion (sample rate, bit depth)
- Batch processing multiple .pgm files
- GUI interface
- Sample preview/audition
- Automatic sample name matching improvements
