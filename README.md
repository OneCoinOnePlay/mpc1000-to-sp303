# MPC1000 to SP-303 Converter

Convert MPC1000 drum programs (.pgm files) to Boss Dr. Sample SP-303 format with automatic sample preprocessing.

## Features

- 🎵 **Parse MPC1000 .pgm files** - Extract all 64 pad assignments
- 📁 **Organize into 8 banks** - Creates Bank_A through Bank_H ready for SP-303
- ⚡ **Auto-pad short samples** - Fixes samples shorter than 110ms (SP-303 requirement)
- ✅ **Tested on real hardware** - Verified working on actual SP-303

## Quick Start

```bash
# 1. Pad any short samples (< 110ms)
python preprocess_sp303_wavs.py ./samples -o ./samples_padded

# 2. Organize into SP-303 banks
python organize_sp303_banks.py VinylDrumsMars1.pgm ./samples_padded ./output

# 3. Transfer Bank_A, Bank_B, etc. to your SP-303
```

## Why This Tool?

The SP-303 has two critical requirements that often cause issues:

1. **Minimum duration:** Samples must be at least 110ms or they won't load
2. **Specific naming:** Files must be named SMPL0001.WAV through SMPL0008.WAV per bank

This toolkit handles both automatically.

## Installation

```bash
git clone https://github.com/OneCoinOnePlay/mpc1000-to-sp303.git
cd mpc1000-to-sp303
```

No dependencies required - uses Python standard library only.

## Requirements

- Python 3.6+
- MPC1000 .pgm file
- WAV files (44.1kHz, 16-bit recommended)

## Usage

### Preprocessing (if you have short samples)

```bash
python preprocess_sp303_wavs.py <input_directory> [-o output_directory]
```

**What it does:**
- Checks all WAV files for duration
- Pads samples < 110ms by adding silence to the end
- Preserves original audio quality
- Flags format issues (sample rate, bit depth)

**Example:**
```bash
python preprocess_sp303_wavs.py ./my_samples -o ./sp303_ready
```

### Organizing into Banks

```bash
python organize_sp303_banks.py <pgm_file> [wav_directory] [output_directory]
```

**What it does:**
- Parses MPC1000 .pgm file structure
- Maps 64 MPC pads to 8 SP-303 banks (8 samples each)
- Renames files to SP-303 format (SMPL0001.WAV, etc.)
- Creates ready-to-transfer bank folders

**Example:**
```bash
python organize_sp303_banks.py VinylDrumsMars1.pgm ./samples ./sp303_banks
```

## Bank Mapping

| SP-303 Bank | MPC Pads | Samples |
|-------------|----------|---------|
| Bank_A | 0-7 | SMPL0001-0008.WAV |
| Bank_B | 8-15 | SMPL0001-0008.WAV |
| Bank_C | 16-23 | SMPL0001-0008.WAV |
| Bank_D | 24-31 | SMPL0001-0008.WAV |
| Bank_E | 32-39 | SMPL0001-0008.WAV |
| Bank_F | 40-47 | SMPL0001-0008.WAV |
| Bank_G | 48-55 | SMPL0001-0008.WAV |
| Bank_H | 56-63 | SMPL0001-0008.WAV |

## SP-303 Audio Specifications

- **Sample Rate:** 44100 Hz (44.1 kHz)
- **Bit Depth:** 16-bit signed integer
- **Channels:** Mono or Stereo
- **Duration:** Minimum 110ms (tested on hardware)

## Troubleshooting

**Samples won't load on SP-303:**
- Check duration: `afinfo SMPL0001.WAV | grep duration` (should show ≥ 0.11 sec)
- Verify format: Should be 44100 Hz, 16-bit
- Ensure proper file naming: SMPL0001.WAV through SMPL0008.WAV

**"NOT FOUND" errors:**
- WAV filenames must match (or contain) sample names from .pgm file
- Script tries exact, case-insensitive, and partial matches

**Format conversion needed:**
If files aren't 44.1kHz/16-bit, use:
```bash
ffmpeg -i input.wav -ar 44100 -sample_fmt s16 output.wav
```

## Documentation

See [COMPLETE_README.md](COMPLETE_README.md) for detailed documentation, examples, and technical details.

## Real-World Testing

This tool was developed and tested with:
- MPC1000 VinylDrumsMars1.pgm program
- Boss Dr. Sample SP-303
- Various sample durations (47ms - several seconds)

The 110ms minimum was determined through actual hardware testing - samples at exactly 100ms sometimes failed to load.

## Technical Details

### MPC1000 .pgm File Format

- Header: `MPC1000 PGM 1.00` at offset 0x04
- Pad entries: 164 bytes (0xA4) apart
- Sample names: 16-byte null-terminated ASCII strings
- Total: 64 pads (4 banks × 16 pads)

### Padding Implementation

Short samples are padded by appending silence (zero bytes) to reach 110ms:
- Target: 4851 frames at 44.1kHz
- Original audio unchanged
- Silence added to end only

## Contributing

Issues and pull requests welcome! This tool was created for the MPC/SP-303 community.

## License

MIT License - See LICENSE file for details

## Acknowledgments

Created for converting MPC1000 programs to SP-303 format. Tested and verified on real hardware.

---

**Made with ❤️ for the SP-303 community**
