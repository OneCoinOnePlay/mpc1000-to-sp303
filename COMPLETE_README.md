# MPC1000 to Boss SP-303 Sample Organizer

Complete toolkit to convert MPC1000 .pgm programs to Boss Dr. Sample SP-303 format.

## Overview

This toolkit includes two scripts:
1. **preprocess_sp303_wavs.py** - Pads samples shorter than 100ms (SP-303 requirement)
2. **organize_sp303_banks.py** - Organizes samples into SP-303 bank folders based on MPC .pgm file

## SP-303 Audio Requirements

The Boss Dr. Sample SP-303 requires:
- **Sample Rate:** 44100 Hz (44.1 kHz)
- **Bit Depth:** 16-bit (Int16)
- **Channels:** Mono (1 ch) or Stereo (2 ch)
- **Duration:** At least 110ms (samples shorter than this won't load!)

> **Note:** While the theoretical minimum is ~100ms, real-world testing showed some samples at exactly 100ms failed to load. We use 110ms to ensure reliability.

## Quick Start

### Step 1: Check Your WAV Files

Use `afinfo` (macOS) or similar tools to check your files:

```bash
afinfo yourfile.wav
```

Look for:
- `Data format: X ch, 44100 Hz, Int16`
- `estimated duration: X sec` (must be ≥ 0.11 sec / 110ms)

**Critical:** If any samples show duration less than 0.11 seconds (110ms), proceed to Step 2.

### Step 2: Pad Short Samples

The SP-303 cannot load samples shorter than ~100ms. This script automatically pads them:

```bash
# Pad short samples in place
python preprocess_sp303_wavs.py /path/to/samples

# Pad to a new directory (preserves originals)
python preprocess_sp303_wavs.py /path/to/samples -o /path/to/padded

# Quiet mode (minimal output)
python preprocess_sp303_wavs.py /path/to/samples -q
```

### Step 3: Organize Into Banks

Parse the .pgm file and create SP-303 bank folders:

```bash
python organize_sp303_banks.py VinylDrumsMars1.pgm /path/to/samples /path/to/output
```

## Detailed Usage

### preprocess_sp303_wavs.py

**Primary function:** Pads samples shorter than 110ms to meet SP-303 minimum duration.

**Arguments:**
```
positional arguments:
  input_dir             Directory containing WAV files

optional arguments:
  -h, --help            Show help message
  -o, --output-dir      Output directory (default: process in place)
  -q, --quiet           Minimal output
```

**Examples:**
```bash
# Check and pad short samples in current directory
python preprocess_sp303_wavs.py .

# Pad samples to a new folder (preserves originals)
python preprocess_sp303_wavs.py ./original_samples -o ./sp303_ready

# Quiet mode with output directory
python preprocess_sp303_wavs.py ./samples -o ./padded -q
```

**What it does:**
- ✓ Checks all WAV files for duration
- ✓ Pads samples shorter than 110ms by adding silence to the end
- ✓ Preserves samples that are already long enough
- ✓ Shows padding information: "47.9ms → 110.0ms"
- ✓ Also checks format (44.1kHz, 16-bit) and flags issues

**Example output:**
```
BD Clean VYN 03.wav:
  1ch, 44100Hz, 16-bit, 47.9ms
  ⚠ Too short for SP-303 (< 110ms)
  Padded: 47.9ms → 110.0ms
```

### organize_sp303_banks.py

Parses MPC1000 .pgm file and creates organized bank folders.

**Arguments:**
```
python organize_sp303_banks.py <pgm_file> [wav_directory] [output_directory]
```

- `pgm_file` - Path to your MPC1000 .pgm file (required)
- `wav_directory` - Directory containing your WAV files (default: current directory)
- `output_directory` - Where to create bank folders (default: current directory)

**Examples:**
```bash
# Basic usage - WAV files in current directory
python organize_sp303_banks.py VinylDrumsMars1.pgm

# WAV files in a specific directory
python organize_sp303_banks.py VinylDrumsMars1.pgm /path/to/samples

# Output to a specific directory
python organize_sp303_banks.py VinylDrumsMars1.pgm ./samples ./output
```

**Output Structure:**
```
output/
├── Bank_A/
│   ├── SMPL0001.WAV  (MPC pad 0)
│   ├── SMPL0002.WAV  (MPC pad 1)
│   └── ...
├── Bank_B/
│   ├── SMPL0001.WAV  (MPC pad 8)
│   └── ...
├── Bank_C/
├── Bank_D/
├── Bank_E/
├── Bank_F/
├── Bank_G/
└── Bank_H/
```

## Complete Workflow Example

```bash
# 1. Check if any samples are too short
afinfo "BD Clean VYN 03.wav"
# Shows: estimated duration: 0.047891 sec  ← Too short! (< 0.11)

# 2. Pad short samples
python preprocess_sp303_wavs.py ./my_samples -o ./sp303_samples

# 3. Organize into banks using your .pgm file
python organize_sp303_banks.py VinylDrumsMars1.pgm ./sp303_samples ./sp303_banks

# 4. Your banks are ready! Transfer Bank_A, Bank_B, etc. to your SP-303
```

## Bank Mapping

The MPC1000 has 64 pads across 4 banks. This maps to 8 SP-303 banks:

| SP-303 Bank | MPC Pads | Contains |
|-------------|----------|----------|
| Bank_A | 0-7 | First 8 samples |
| Bank_B | 8-15 | Next 8 samples |
| Bank_C | 16-23 | Next 8 samples |
| Bank_D | 24-31 | Next 8 samples |
| Bank_E | 32-39 | Next 8 samples |
| Bank_F | 40-47 | Next 8 samples |
| Bank_G | 48-55 | Next 8 samples |
| Bank_H | 56-63 | Last 8 samples |

## Why Padding is Necessary

The SP-303 has a hardware limitation where it cannot load samples shorter than approximately 110ms. This is common with:
- **Short drum hits** (kicks, snares, hi-hats)
- **Stabs and one-shots**
- **Heavily trimmed samples**

Without padding, these samples simply won't load into the SP-303. The preprocessing script solves this by adding silence to the end, making them exactly 110ms (4851 samples at 44.1kHz).

> **Real-world testing:** Initial attempts at 100ms (4410 samples) showed some samples still failed to load. The 110ms minimum has been tested and verified to work reliably.

## Troubleshooting

### "NOT FOUND" errors when organizing

The script couldn't find a matching WAV file for that sample name.

**Solutions:**
- Make sure WAV filenames match (or contain) the sample names from the .pgm
- WAV files should have a .wav or .WAV extension
- Try renaming your WAV files to match the sample names shown in the output
- The script tries exact match, case-insensitive match, and partial match

### Samples still won't load on SP-303

**Check duration:**
```bash
afinfo SMPL0001.WAV | grep duration
```
Should show at least 0.11 seconds (110ms).

**Check format:**
```bash
afinfo SMPL0001.WAV | grep "Data format"
```
Should show `44100 Hz, Int16`.

**If format is wrong:**
The preprocessing script will flag format issues but won't auto-convert (to preserve quality). Use professional tools:
```bash
# Using ffmpeg (recommended)
ffmpeg -i input.wav -ar 44100 -sample_fmt s16 output.wav

# Using sox
sox input.wav -r 44100 -b 16 output.wav
```

### Memory card issues

- SP-303 memory cards must be formatted correctly (FAT16/FAT32)
- Some older SP-303 units have specific card size limitations
- Try smaller batches if loading all banks at once fails

## Technical Details

### Padding Methodology

When a sample is shorter than 110ms:
1. Calculate target frames: `0.11 seconds × 44100 Hz = 4851 frames`
2. Calculate silence needed: `4851 - current_frames`
3. Append silence bytes (zeros) to the end of the sample
4. Original audio is preserved; only silence is added

The 110ms minimum was determined through real-world testing on actual SP-303 hardware.

### MPC1000 .pgm File Structure

- **Header:** `MPC1000 PGM 1.00` at offset 0x04
- **First pad entry:** offset 0x18
- **Pad entry size:** 164 bytes (0xA4)
- **Sample name:** First 16 bytes of each pad entry (null-terminated ASCII)
- **Total pads:** 64 (4 banks × 16 pads)

## Requirements

- Python 3.6 or higher
- No external dependencies (uses Python standard library only)
- For format conversion: ffmpeg or sox (optional, only if files aren't 44.1kHz/16-bit)

## License

This toolkit is provided as-is for personal use.

## Credits

Developed for converting MPC1000 drum programs to Boss Dr. Sample SP-303 format.
