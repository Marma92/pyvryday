# Audio Cover Processor for FIIO Snowsky Echo Mini

A Python script that automatically processes and optimizes album cover art for music libraries, specifically designed for the FIIO Snowsky Echo Mini portable music player.

## Features

- **Automatic Cover Detection**: Scans music directories for existing cover art files
- **Audio Metadata Extraction**: Extracts embedded cover art from FLAC and MP3 files
- **Online Cover Fetching**: Downloads missing covers from MusicBrainz and Cover Art Archive
- **Image Optimization**: Resizes and crops covers to 160x160 pixels (optimal for FIIO players)
- **Metadata Injection**: Embeds processed covers back into audio files
- **Colored Logging**: Real-time progress tracking with color-coded output
- **Network Awareness**: Checks internet connectivity before attempting downloads

## Requirements

### Python Dependencies
```bash
pip install requests pillow mutagen
```

### Supported Formats
- **Audio**: FLAC, MP3
- **Images**: JPG, JPEG, PNG

## Installation

1. Clone or download the script:
```bash
git clone <repository-url>
cd audio_covers
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Make the script executable:
```bash
chmod +x resize_covers.py
```

## Usage

### Basic Usage
Run the script in your music library directory:
```bash
python resize_covers.py
```

The script will:
- Recursively scan all subdirectories
- Process each directory containing audio files
- Generate a final report with statistics

### Processing Logic

For each directory containing audio files, the script follows this priority:

1. **Local Image Files**: Checks for existing cover images (cover.jpg, folder.jpg, etc.)
2. **Embedded Audio Covers**: Extracts covers from FLAC/MP3 metadata
3. **Online Download**: Fetches covers from MusicBrainz if artist/album metadata is available
4. **Image Processing**: Resizes and crops to 160x160 pixels with center cropping
5. **Metadata Injection**: Embeds the final cover back into all audio files

### Configuration

Key settings in the script (lines 35-51):

```python
TARGET_SIZE = (160, 160)          # FIIO optimal resolution
COVER_FILENAME = "cover.jpg"      # Output filename
MAX_RETRIES = 3                   # Download retry attempts
INITIAL_DELAY = 1.0              # Initial retry delay (seconds)
```

## Output

### Console Output
The script provides real-time colored logging:
- 🔵 **[COVER]**: Cover art operations
- 🟣 **[AUDIO]**: Audio file processing
- 🟦 **[DIR]**: Directory scanning
- 🟢 **[INFO]**: General information
- 🟠 **[WARN]**: Warnings
- 🔴 **[ERROR]**: Errors

### Final Report
```
=== Final report ===
covers_downloaded: 15
covers_written: 42
audio_updated: 128
Directories processed: 45
Total time: 123.45s
```

## How It Works

### 1. Directory Scanning
- Recursively walks through all subdirectories
- Identifies audio files (.flac, .mp3) and image files (.jpg, .jpeg, .png)
- Skips directories without audio files

### 2. Cover Acquisition Priority
1. **Local Images**: Uses existing image files if they meet size requirements
2. **Audio Metadata**: Extracts embedded covers from audio files
3. **Online Sources**: Queries MusicBrainz API for missing covers
4. **Fallback**: Logs warning if no cover is found

### 3. Image Processing
- Converts all images to RGB JPEG format
- Performs center cropping to square aspect ratio
- Resizes to 160x160 pixels using LANCZOS resampling
- Maintains 90% JPEG quality for optimal file size/quality balance

### 4. Metadata Injection
- **FLAC**: Updates picture block in Vorbis comments
- **MP3**: Updates APIC frame in ID3 tags
- Preserves all other metadata

### 5. Online Cover Fetching
- Normalizes album names (removes parenthetical information)
- Queries MusicBrainz release and release-group APIs
- Downloads front cover from Cover Art Archive
- Implements exponential backoff retry logic

## Error Handling

- Network timeouts and connection errors
- Corrupted audio files
- Missing metadata
- Invalid image formats
- API rate limiting

## Performance

- Processes multiple audio files per directory in parallel
- Implements rate limiting between directory processing
- Caches network requests when possible
- Optimized for large music libraries

## Compatibility

- **FIIO Snowsky Echo Mini**: Optimized for 160x160 display resolution
- **Other FIIO Players**: Compatible with most FIIO portable players
- **General Use**: Works with any music library requiring standardized cover art

## Troubleshooting

### No Covers Found
- Check if audio files contain artist/album metadata
- Verify internet connectivity for online downloads
- Ensure image files meet minimum size requirements

### Permission Errors
- Run with appropriate file system permissions
- Ensure write access to music directories

### Network Issues
- Script automatically detects offline mode
- Retries failed downloads with exponential backoff

## License

Personal use script created for FIIO Snowsky Echo Mini optimization.

## Contributing

Feel free to modify the configuration settings to suit your specific device requirements or personal preferences.