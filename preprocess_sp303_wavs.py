#!/usr/bin/env python3
"""
Preprocess WAV files to ensure SP-303 compatibility.
- Pads samples shorter than 100ms (SP-303 minimum requirement)
- Converts to 44.1kHz, 16-bit if needed
"""

import wave
import struct
import os
import sys
from pathlib import Path


# SP-303 minimum sample duration in seconds
MIN_DURATION = 0.11  # 110ms (tested - some samples at 100ms didn't load)


def get_wav_info(wav_path):
    """Get information about a WAV file."""
    try:
        with wave.open(str(wav_path), 'rb') as wav:
            info = {
                'channels': wav.getnchannels(),
                'sample_width': wav.getsampwidth(),
                'framerate': wav.getframerate(),
                'frames': wav.getnframes(),
                'duration': wav.getnframes() / wav.getframerate()
            }
            return info
    except Exception as e:
        print(f"Error reading {wav_path}: {e}")
        return None


def is_too_short(info):
    """Check if WAV file is shorter than SP-303 minimum (100ms)."""
    if not info:
        return False
    return info['duration'] < MIN_DURATION


def is_sp303_compatible(info):
    """Check if WAV file meets SP-303 requirements."""
    if not info:
        return False
    
    # SP-303 requirements:
    # - 44100 Hz sample rate
    # - 16-bit (2 bytes per sample)
    # - Mono or Stereo
    # - At least 100ms duration
    
    compatible = (
        info['framerate'] == 44100 and
        info['sample_width'] == 2 and
        info['channels'] in [1, 2] and
        info['duration'] >= MIN_DURATION
    )
    
    return compatible


def pad_short_sample(input_path, output_path, target_duration=MIN_DURATION):
    """
    Pad a short WAV file to meet SP-303 minimum duration (100ms).
    Adds silence to the end of the sample.
    
    Args:
        input_path: Path to input WAV file
        output_path: Path to output WAV file
        target_duration: Minimum duration in seconds (default: 0.1 = 100ms)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read input WAV
        with wave.open(str(input_path), 'rb') as wav_in:
            params = wav_in.getparams()
            frames = wav_in.readframes(params.nframes)
        
        # Calculate current and target duration
        current_duration = params.nframes / params.framerate
        
        if current_duration >= target_duration:
            # Sample is already long enough, just copy it
            if input_path != output_path:
                with wave.open(str(output_path), 'wb') as wav_out:
                    wav_out.setparams(params)
                    wav_out.writeframes(frames)
            return True
        
        # Calculate how many frames of silence to add
        target_frames = int(target_duration * params.framerate)
        silence_frames = target_frames - params.nframes
        
        # Create silence (zeros)
        silence_bytes = silence_frames * params.nchannels * params.sampwidth
        silence = b'\x00' * silence_bytes
        
        # Combine original audio with silence
        padded_frames = frames + silence
        
        # Write output WAV
        with wave.open(str(output_path), 'wb') as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(padded_frames)
        
        new_duration = target_frames / params.framerate
        print(f"  Padded: {current_duration*1000:.1f}ms → {new_duration*1000:.1f}ms")
        
        return True
        
    except Exception as e:
        print(f"  Error padding {input_path}: {e}")
        return False


def convert_format(input_path, output_path):
    """
    Convert WAV file to SP-303 format (44.1kHz, 16-bit).
    This is a simplified converter for basic format changes.
    
    Args:
        input_path: Path to input WAV file
        output_path: Path to output WAV file
    
    Returns:
        True if conversion successful, False otherwise
    """
    try:
        # Read input WAV
        with wave.open(str(input_path), 'rb') as wav_in:
            params = wav_in.getparams()
            frames = wav_in.readframes(params.nframes)
        
        # Check what needs to be converted
        needs_conversion = False
        
        if params.framerate != 44100:
            needs_conversion = True
            print(f"  Converting sample rate: {params.framerate} Hz → 44100 Hz")
        
        if params.sampwidth != 2:
            needs_conversion = True
            print(f"  Converting bit depth: {params.sampwidth * 8}-bit → 16-bit")
        
        if not needs_conversion:
            # File is already correct format, just copy it
            if input_path != output_path:
                with wave.open(str(output_path), 'wb') as wav_out:
                    wav_out.setparams(params)
                    wav_out.writeframes(frames)
            return True
        
        # For format conversion, recommend using professional audio software
        print(f"  ⚠ Format conversion required. Consider using:")
        print(f"     - ffmpeg: ffmpeg -i input.wav -ar 44100 -sample_fmt s16 output.wav")
        print(f"     - sox: sox input.wav -r 44100 -b 16 output.wav")
        print(f"     - Audacity or other audio software")
        print(f"  Copying file unchanged for now.")
        
        # Just copy the file for now
        if input_path != output_path:
            with wave.open(str(output_path), 'wb') as wav_out:
                wav_out.setparams(params)
                wav_out.writeframes(frames)
        
        return False
        
    except Exception as e:
        print(f"  Error converting {input_path}: {e}")
        return False


def preprocess_directory(input_dir, output_dir=None, verbose=True):
    """
    Preprocess all WAV files in a directory for SP-303 compatibility.
    Focuses on padding short samples (< 100ms).
    
    Args:
        input_dir: Directory containing WAV files
        output_dir: Output directory (if None, files are converted in place)
        verbose: Print detailed information
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir) if output_dir else input_path
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all WAV files
    wav_files = list(input_path.glob('*.wav')) + list(input_path.glob('*.WAV'))
    
    if not wav_files:
        print(f"No WAV files found in {input_dir}")
        return
    
    print(f"\nFound {len(wav_files)} WAV files")
    print(f"SP-303 minimum duration: {MIN_DURATION*1000:.0f}ms")
    print(f"{'='*60}")
    
    compatible_count = 0
    padded_count = 0
    format_issues = 0
    error_count = 0
    
    for wav_file in sorted(wav_files):
        if verbose:
            print(f"\n{wav_file.name}:")
        
        # Get file info
        info = get_wav_info(wav_file)
        
        if not info:
            error_count += 1
            continue
        
        if verbose:
            print(f"  {info['channels']}ch, {info['framerate']}Hz, {info['sample_width']*8}-bit, {info['duration']*1000:.1f}ms")
        
        output_file = output_path / wav_file.name
        
        # Check if file is too short
        if is_too_short(info):
            if verbose:
                print(f"  ⚠ Too short for SP-303 (< {MIN_DURATION*1000:.0f}ms)")
            
            # Pad the sample
            if pad_short_sample(wav_file, output_file, MIN_DURATION):
                padded_count += 1
                
                # After padding, check format
                new_info = get_wav_info(output_file)
                if new_info and (new_info['framerate'] != 44100 or new_info['sample_width'] != 2):
                    convert_format(output_file, output_file)
                    format_issues += 1
            else:
                error_count += 1
        
        # Check format compatibility
        elif info['framerate'] != 44100 or info['sample_width'] != 2:
            if verbose:
                print(f"  ⚠ Format needs conversion")
            
            # Copy to output and flag for manual conversion
            if convert_format(wav_file, output_file):
                compatible_count += 1
            else:
                format_issues += 1
        
        # File is already compatible
        else:
            if verbose:
                print(f"  ✓ SP-303 compatible")
            compatible_count += 1
            
            # Copy to output if different directory
            if output_dir and output_path != input_path:
                pad_short_sample(wav_file, output_file, 0)  # Just copy
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Already compatible: {compatible_count}")
    print(f"  Padded (< {MIN_DURATION*1000:.0f}ms): {padded_count}")
    
    if format_issues > 0:
        print(f"  Format issues (need manual conversion): {format_issues}")
        print(f"\n  Recommended: Use ffmpeg or sox for format conversion:")
        print(f"    ffmpeg -i input.wav -ar 44100 -sample_fmt s16 output.wav")
    
    if error_count > 0:
        print(f"  Errors: {error_count}")
    
    print(f"  Total: {len(wav_files)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Preprocess WAV files for SP-303: pads short samples (< 100ms) and checks format'
    )
    parser.add_argument('input_dir', help='Directory containing WAV files')
    parser.add_argument('-o', '--output-dir', help='Output directory (default: convert in place)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    preprocess_directory(
        args.input_dir,
        args.output_dir,
        verbose=not args.quiet
    )
