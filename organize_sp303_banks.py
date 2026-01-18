#!/usr/bin/env python3
"""
Parse MPC1000 .pgm file and organize WAV files for Boss Dr. Sample SP-303.
Creates Bank_A through Bank_H folders with 8 samples each (SMPL0001.WAV to SMPL0008.WAV).

IMPORTANT: WAV files must be SP-303 compatible:
- 44100 Hz sample rate
- 16-bit (Int16)
- Mono or Stereo

If your WAV files need conversion, run preprocess_sp303_wavs.py first.
"""

import struct
import os
import shutil
from pathlib import Path


def parse_pgm_file(pgm_path):
    """Parse MPC1000 .pgm file and extract sample names and pad assignments."""
    
    with open(pgm_path, 'rb') as f:
        data = f.read()
    
    # Check header
    header = data[4:20].decode('ascii', errors='ignore')
    if 'MPC1000 PGM' not in header:
        raise ValueError(f"Not a valid MPC1000 PGM file: {header}")
    
    print(f"Header: {header}")
    
    # MPC1000 .pgm file structure:
    # - First sample name starts at 0x18
    # - Each pad entry is exactly 0xA4 (164) bytes apart
    # - Sample name is 16 bytes at the start of each entry
    
    pads = {}
    PAD_ENTRY_SIZE = 0xA4  # 164 bytes between samples
    FIRST_SAMPLE_OFFSET = 0x18
    SAMPLE_NAME_SIZE = 16
    
    pad_index = 0
    offset = FIRST_SAMPLE_OFFSET
    
    while offset + SAMPLE_NAME_SIZE <= len(data) and pad_index < 64:
        # Extract sample name (16 bytes)
        sample_name_raw = data[offset:offset+SAMPLE_NAME_SIZE]
        
        try:
            # Decode and clean the sample name - remove all non-printable chars
            sample_name = ''
            for byte in sample_name_raw:
                if 32 <= byte <= 126:  # Printable ASCII range
                    sample_name += chr(byte)
                elif byte == 0:  # Null terminator
                    break
            
            sample_name = sample_name.strip()
            
            # Check if we've reached the end (empty or invalid entry)
            if not sample_name or len(sample_name) < 2:
                # Try a few more entries in case of gaps
                if pad_index > 0:
                    pad_index += 1
                    offset += PAD_ENTRY_SIZE
                    continue
                else:
                    break
            
            pads[pad_index] = sample_name
            print(f"Pad {pad_index:2d}: {sample_name}")
            pad_index += 1
            
        except Exception as e:
            print(f"Error at offset 0x{offset:04x}: {e}")
            break
        
        # Move to next pad entry
        offset += PAD_ENTRY_SIZE
    
    print(f"\nTotal pads found: {len(pads)}")
    return pads


def find_wav_file(sample_name, wav_dir):
    """Find matching WAV file for a sample name."""
    # Clean up the sample name
    sample_name_clean = sample_name.strip()
    
    # Look for exact match first
    wav_path = Path(wav_dir) / f"{sample_name_clean}.wav"
    if wav_path.exists():
        return wav_path
    
    # Try case-insensitive search
    for wav_file in Path(wav_dir).glob("*.wav"):
        if wav_file.stem.lower() == sample_name_clean.lower():
            return wav_file
    
    # Try partial match
    for wav_file in Path(wav_dir).glob("*.wav"):
        if sample_name_clean.lower() in wav_file.stem.lower():
            return wav_file
    
    return None


def create_sp303_banks(pgm_path, wav_dir, output_dir):
    """Create SP-303 bank folders with organized samples."""
    
    # Parse the .pgm file
    print("Parsing .pgm file...")
    pads = parse_pgm_file(pgm_path)
    
    print(f"\nFound {len(pads)} pads")
    
    # Create all 8 banks (A-H) for the 64 pads
    # Each bank has 8 pads
    bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    
    for bank_idx, bank_name in enumerate(bank_names):
        bank_dir = Path(output_dir) / f"Bank_{bank_name}"
        bank_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n=== Creating Bank {bank_name} ===")
        
        for pad_in_bank in range(8):
            # Calculate the global pad number
            # Bank A = pads 0-7, Bank B = pads 8-15, etc.
            global_pad_num = bank_idx * 8 + pad_in_bank
            
            if global_pad_num in pads:
                sample_name = pads[global_pad_num]
                wav_file = find_wav_file(sample_name, wav_dir)
                
                if wav_file:
                    dest = bank_dir / f"SMPL{pad_in_bank+1:04d}.WAV"
                    shutil.copy2(wav_file, dest)
                    print(f"Pad {pad_in_bank+1}: {sample_name} -> {dest.name}")
                else:
                    print(f"Pad {pad_in_bank+1}: {sample_name} -> NOT FOUND")
            else:
                print(f"Pad {pad_in_bank+1}: No assignment")
        
        print(f"✓ Bank_{bank_name} created in: {bank_dir}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python organize_sp303_banks.py <pgm_file> [wav_directory] [output_directory]")
        print("\nExample:")
        print("  python organize_sp303_banks.py VinylDrumsMars1.pgm . ./output")
        sys.exit(1)
    
    pgm_file = sys.argv[1]
    wav_directory = sys.argv[2] if len(sys.argv) > 2 else "."
    output_directory = sys.argv[3] if len(sys.argv) > 3 else "."
    
    create_sp303_banks(pgm_file, wav_directory, output_directory)
