# Audio Cover Processor for FIIO Snowsky Echo Mini

A Python script that automatically processes and optimizes album cover art for music libraries, specifically designed for the FIIO Snowsky Echo Mini portable music player.

## Features

- **Smart Cover.jpg Processing**: Checks and resizes existing cover.jpg files if larger than 160x160
- **Individual Audio File Analysis**: Examines every audio file for oversized cover metadata
- **Automatic Metadata Standardization**: Replaces oversized covers with optimized 160x160 versions
- **Cover Creation**: Generates cover.jpg from audio metadata when missing
- **Online Cover Fetching**: Downloads missing covers from MusicBrainz and Cover Art Archive
- **Image Optimization**: Resizes and crops covers to 160x160 pixels (optimal for FIIO players)
- **Comprehensive Logging**: Detailed logging of every action performed
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

The script follows a precise workflow for each directory containing audio files:

#### Step 1: Cover.jpg Analysis
- Checks if `cover.jpg` exists in the folder
- Measures the exact dimensions of the existing cover
- **If size > 160x160**: Resizes the cover.jpg to 160x160 pixels and replaces the original file
- **If size ≤ 160x160**: Uses the existing cover as-is (no changes needed)

#### Step 2: Audio File Metadata Inspection
- Examines every audio file (.flac, .mp3) in the directory individually
- Extracts current cover art from metadata
- Measures the dimensions of each embedded cover
- Identifies files that need updates (covers larger than 160x160 or missing covers)

#### Step 3: Cover Creation (if needed)
- If no `cover.jpg` exists but audio files have oversized covers:
  - Creates a new `cover.jpg` from the first available audio cover
  - Resizes it to 160x160 pixels
- If no local covers are available:
  - Attempts online download from MusicBrainz
  - Creates `cover.jpg` from downloaded cover

#### Step 4: Metadata Standardization
- Uses the processed `cover.jpg` (160x160) to update all audio files that need it
- Replaces oversized covers in audio metadata with the standardized version
- Ensures all audio files in the directory have consistent 160x160 covers

#### Step 5: Comprehensive Logging
- Logs every action: file discovery, size checking, resizing, metadata updates
- Reports current dimensions before processing
- Shows which files were updated and why
- Provides summary statistics for each directory

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
The script provides comprehensive real-time colored logging:

#### Log Categories
- 🔵 **[COVER]**: Cover.jpg operations (discovery, resizing, creation)
- 🟣 **[AUDIO]**: Audio file processing (metadata analysis, updates)
- 🟦 **[DIR]**: Directory scanning and processing summaries
- 🟢 **[INFO]**: General information and status updates
- 🟠 **[WARN]**: Warnings about missing files or failed operations
- 🔴 **[ERROR]**: Critical errors and exceptions

#### Example Log Output
```
2024-01-24 10:30:15 | INFO     | [DIR] Processing: /music/Artist/Album
2024-01-24 10:30:15 | INFO     | [COVER] Found cover.jpg with size 1200x1200
2024-01-24 10:30:15 | INFO     | [COVER] Resizing cover.jpg from 1200x1200 to 160x160
2024-01-24 10:30:15 | INFO     | [COVER] Updated cover.jpg to 160x160
2024-01-24 10:30:16 | INFO     | [AUDIO] track01.flac has cover 800x800
2024-01-24 10:30:16 | INFO     | [AUDIO] track01.flac needs cover update (oversized)
2024-01-24 10:30:16 | INFO     | [AUDIO] Cover metadata fixed: track01.flac
2024-01-24 10:30:16 | INFO     | [DIR] Updated covers for 12 audio files
```

### Final Report
```
=== Final report ===
covers_downloaded: 15
covers_written: 42
audio_updated: 128
Directories processed: 45
Total time: 123.45s
```

#### Statistics Explained
- **covers_downloaded**: Number of covers fetched from online sources
- **covers_written**: Number of cover.jpg files created/updated
- **audio_updated**: Number of audio files with updated metadata
- **Directories processed**: Total directories scanned
- **Total time**: Overall processing duration

## How It Works

### 1. Directory Scanning
- Recursively walks through all subdirectories
- Identifies audio files (.flac, .mp3) in each directory
- Skips directories without audio files (logs this action)

### 2. Cover.jpg Processing
- **Discovery**: Checks for existing `cover.jpg` file
- **Size Analysis**: Measures exact dimensions (e.g., "Found cover.jpg with size 1200x1200")
- **Conditional Resizing**: 
  - If dimensions > 160x160: Resizes and replaces original file
  - If dimensions ≤ 160x160: Leaves unchanged
- **Logging**: Reports all actions taken

### 3. Audio File Analysis
- **Individual Inspection**: Examines every audio file separately
- **Metadata Extraction**: Pulls embedded cover art from FLAC/MP3 files
- **Size Measurement**: Logs current cover dimensions for each file
- **Update Identification**: Flags files needing metadata updates

### 4. Cover Creation Logic
- **From Audio Metadata**: If no `cover.jpg` exists but audio files have covers
  - Extracts cover from first suitable audio file
  - Resizes to 160x160 pixels
  - Saves as new `cover.jpg`
- **Online Download**: If no local covers available
  - Searches MusicBrainz using artist/album metadata
  - Downloads and resizes to 160x160
  - Creates `cover.jpg` file

### 5. Metadata Standardization
- **Batch Updates**: Applies standardized cover to all files needing updates
- **Size Enforcement**: Ensures all audio metadata contains 160x160 covers
- **Format Preservation**: Maintains original audio format and quality
- **Progress Logging**: Reports each file update

### 6. Image Processing Details
- **Resampling**: Uses LANCZOS resampling for high-quality downscaling
- **Aspect Ratio**: Maintains square aspect ratio with center cropping
- **Format**: Converts to RGB JPEG with 90% quality
- **Optimization**: Balanced file size and image quality

### 7. Online Cover Fetching
- **Metadata Requirements**: Needs artist and album information
- **API Integration**: MusicBrainz release and release-group APIs
- **Cover Source**: Cover Art Archive for front covers
- **Retry Logic**: Exponential backoff for failed requests

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
- Check if audio files contain artist/album metadata (required for online downloads)
- Verify internet connectivity for online downloads
- Ensure image files meet minimum size requirements (≥160x160)

### Permission Errors
- Run with appropriate file system permissions
- Ensure write access to music directories (needed for cover.jpg updates)
- Check that audio files are not read-only

### Large Cover Files Not Resizing
- Verify the cover.jpg file exists and is readable
- Check that the file is a valid image format (JPG, JPEG, PNG)
- Ensure the file dimensions are actually larger than 160x160

### Audio Files Not Updating
- Check that audio files have embedded covers larger than 160x160
- Verify the files are not corrupted or locked by other applications
- Ensure proper mutagen library installation

### Network Issues
- Script automatically detects offline mode and skips online downloads
- Retries failed downloads with exponential backoff (up to 3 attempts)
- Check MusicBrainz API status if downloads consistently fail

### Performance Issues
- Script processes directories sequentially with small delays
- Large libraries may take considerable time
- Consider running on a subset of directories first

## Advanced Usage

### Selective Processing
The script processes all directories recursively. To process specific directories:
```bash
cd /path/to/your/music/Artist/Album
python /path/to/resize_covers.py
```

### Dry Run Analysis
To see what would be processed without making changes, temporarily comment out the `inject_cover()` calls in the script.

### Custom Target Size
Modify the `TARGET_SIZE` variable at the top of the script for different devices:
```python
TARGET_SIZE = (300, 300)  # For higher resolution devices
TARGET_SIZE = (128, 128)  # For smaller displays
```

## Script Behavior

### What the Script Does
1. **Scans** every directory containing audio files
2. **Checks** existing cover.jpg files for size compliance
3. **Resizes** oversized cover.jpg files to 160x160
4. **Analyzes** every audio file's embedded cover dimensions
5. **Creates** cover.jpg from audio metadata when missing
6. **Downloads** covers online when no local options exist
7. **Updates** audio metadata with standardized 160x160 covers
8. **Logs** every action performed with detailed information

### What the Script Does NOT Do
- Delete original audio files or other metadata
- Modify audio quality or format
- Process directories without audio files
- Resize covers that are already 160x160 or smaller
- Update audio files that already have properly sized covers

## License

Personal use script created for FIIO Snowsky Echo Mini optimization.

## Contributing

Feel free to modify the configuration settings to suit your specific device requirements or personal preferences. The script is designed to be easily adaptable for different target sizes and audio formats.