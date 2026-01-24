#!/usr/bin/env python3
import os
import re
import time
import logging
import socket
import random
from io import BytesIO
from collections import defaultdict
from pathlib import Path

# ANSI color codes
class Colors:
    RED = '\033[91m'
    ORANGE = '\033[93m'
    YELLOW = '\033[33m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

import requests
from PIL import Image
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC
from mutagen.wave import WAVE

# ============================================================
# CONFIGURATION
# ============================================================

TARGET_SIZE = (160, 160)
COVER_FILENAME = "cover.jpg"

SUPPORTED_AUDIO = (".flac", ".mp3", ".wav")
SUPPORTED_IMAGES = (".jpg", ".jpeg", ".png")

MB_HEADERS = {
    "User-Agent": "EchoMiniCoverTool/1.0 (personal-use)"
}

MB_RELEASE_SEARCH = "https://musicbrainz.org/ws/2/release/"
MB_RG_SEARCH = "https://musicbrainz.org/ws/2/release-group/"
CAA_BASE = "https://coverartarchive.org"

MAX_RETRIES = 3
INITIAL_DELAY = 1.0  # seconds
PAUSE_BETWEEN_DIRS = 0.2  # seconds

# ============================================================
# LOGGING
# ============================================================

class ColoredFormatter(logging.Formatter):
    def __init__(self):
        super().__init__("%(asctime)s | %(levelname)-8s | %(message)s")
        
    def format(self, record):
        # Get the original message
        message = record.getMessage()
        
        # If message contains a prefix like [COVER], [AUDIO], etc., color it
        if ']' in message and '[' in message:
            parts = message.split(']', 1)
            if len(parts) == 2:
                category = parts[0] + ']'
                content = parts[1].strip()
                
                # Color category based on type
                if '[ERROR]' in category:
                    category = f"{Colors.RED}{category}{Colors.RESET}"
                elif '[WARN]' in category:
                    category = f"{Colors.ORANGE}{category}{Colors.RESET}"
                elif '[COVER]' in category:
                    category = f"{Colors.BLUE}{category}{Colors.RESET}"
                elif '[AUDIO]' in category:
                    category = f"{Colors.PURPLE}{category}{Colors.RESET}"
                elif '[DIR]' in category:
                    category = f"{Colors.CYAN}{category}{Colors.RESET}"
                else:
                    category = f"{Colors.GREEN}{category}{Colors.RESET}"
                
                message = f"{category} {content}"
        
        # Format with timestamp and level
        timestamp = self.formatTime(record, self.datefmt)
        level = record.levelname
        
        # Color the level
        if record.levelno >= logging.ERROR:
            level = f"{Colors.RED}{level}{Colors.RESET}"
        elif record.levelno >= logging.WARNING:
            level = f"{Colors.ORANGE}{level}{Colors.RESET}"
        elif record.levelno >= logging.INFO:
            level = f"{Colors.GREEN}{level}{Colors.RESET}"
        else:
            level = f"{Colors.CYAN}{level}{Colors.RESET}"
        
        return f"{timestamp} | {level:<8} | {message}"

# Configure logging with colored formatter
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger = logging.getLogger("cover")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

# ============================================================
# STATS
# ============================================================

stats = defaultdict(int)
folder_timings = {}

# ============================================================
# UTILS
# ============================================================

def is_online(timeout=2):
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout)
        return True
    except OSError:
        return False

def normalize_album(album):
    if not album:
        return None
    album = re.sub(r"\(.*?\)", "", album)
    album = re.sub(r"\[.*?\]", "", album)
    album = album.split(" - ")[0]
    return album.strip()

def resize_image(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    
    # Crop to square if needed
    width, height = img.size
    if width != height:
        # Calculate crop box for center crop
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        img = img.crop((left, top, right, bottom))
    
    # Resize to target square size
    img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    out = BytesIO()
    img.save(out, format="JPEG", quality=90)
    return out.getvalue(), img.size

def image_is_too_small(image_bytes):
    img = Image.open(BytesIO(image_bytes))
    return img.width < TARGET_SIZE[0] or img.height < TARGET_SIZE[1]

# ============================================================
# MUSICBRAINZ / COVER ART ARCHIVE
# ============================================================

def mb_search_release(artist, album):
    album = normalize_album(album)
    if not artist or not album:
        return None
    query = f'artist:"{artist}" AND release:{album}'
    params = {"query": query, "fmt": "json", "limit": 1}
    r = requests.get(MB_RELEASE_SEARCH, params=params, headers=MB_HEADERS, timeout=5)
    r.raise_for_status()
    releases = r.json().get("releases", [])
    if releases:
        return releases[0]["id"], "release"
    return None

def mb_search_release_group(artist, album):
    album = normalize_album(album)
    if not artist or not album:
        return None
    query = f'artist:"{artist}" AND releasegroup:{album}'
    params = {"query": query, "fmt": "json", "limit": 1}
    r = requests.get(MB_RG_SEARCH, params=params, headers=MB_HEADERS, timeout=5)
    r.raise_for_status()
    groups = r.json().get("release-groups", [])
    if groups:
        return groups[0]["id"], "release-group"
    return None

def fetch_cover_from_caa(mbid, mbid_type):
    url = f"{CAA_BASE}/{mbid_type}/{mbid}/front"
    delay = INITIAL_DELAY
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return r.content
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES:
                raise
            logger.warning(
                f"[COVER] CAA failed attempt {attempt}/{MAX_RETRIES}, retry in {delay:.1f}s ({e})"
            )
            time.sleep(delay)
            delay *= 2 + random.uniform(0, 0.5)
    return None

def fetch_cover_online(artist, album):
    logger.info(f"[COVER] Searching online: {artist} / {album}")
    try:
        result = mb_search_release(artist, album)
        if not result:
            logger.info("[COVER] Release not found, trying release-group")
            result = mb_search_release_group(artist, album)
        if not result:
            logger.warning("[COVER] No MusicBrainz results")
            return None
        mbid, mbid_type = result
        logger.info(f"[COVER] Cover found via {mbid_type}")
        img = fetch_cover_from_caa(mbid, mbid_type)
        stats["covers_downloaded"] += 1
        return img
    except Exception as e:
        logger.warning(f"[COVER] Failed to fetch online cover: {e}")
        return None

# ============================================================
# AUDIO HANDLING
# ============================================================

def extract_audio_cover(path):
    try:
        if path.endswith(".flac"):
            audio = FLAC(path)
            if audio.pictures:
                return audio.pictures[0].data
        elif path.endswith(".mp3"):
            audio = MP3(path, ID3=ID3)
            if not audio.tags:
                return None
            for tag in audio.tags.values():
                if hasattr(tag, 'data'):  # Check if it's an APIC frame
                    return tag.data
        elif path.endswith(".wav"):
            audio = WAVE(path)
            if not audio.tags:
                return None
            for tag in audio.tags.values():
                if hasattr(tag, 'data'):  # Check if it's an APIC frame
                    return tag.data
    except Exception as e:
        logger.warning(f"[AUDIO] Failed to read cover: {path} ({e})")
    return None

def inject_cover(path, image_bytes):
    try:
        if path.endswith(".flac"):
            audio = FLAC(path)
            audio.clear_pictures()
            pic = Picture()
            pic.data = image_bytes
            pic.type = 3
            pic.mime = "image/jpeg"
            audio.add_picture(pic)
            audio.save()
        elif path.endswith(".mp3"):
            audio = MP3(path, ID3=ID3)
            if audio.tags is None:
                audio.add_tags()
                # After add_tags(), tags should be available
                if audio.tags is None:
                    logger.warning(f"[AUDIO] Failed to create tags for {path}")
                    return
            
            # Clear existing APIC tags
            audio.tags.delall("APIC")
            
            # Add new APIC tag
            apic = APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=image_bytes)
            try:
                audio.tags.add(apic)
            except:
                # Alternative method for different mutagen versions
                try:
                    audio.tags["APIC:Cover"] = apic
                except Exception as e:
                    logger.warning(f"[AUDIO] Failed to add APIC tag: {e}")
                    return
            audio.save()
        elif path.endswith(".wav"):
            audio = WAVE(path)
            if audio.tags is None:
                audio.add_tags()
                # After add_tags(), tags should be available
                if audio.tags is None:
                    logger.warning(f"[AUDIO] Failed to create tags for {path}")
                    return
            
            # Clear existing APIC tags
            audio.tags.delall("APIC")
            
            # Add new APIC tag
            apic = APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=image_bytes)
            try:
                audio.tags.add(apic)
            except:
                # Alternative method for different mutagen versions
                try:
                    audio.tags["APIC:Cover"] = apic
                except Exception as e:
                    logger.warning(f"[AUDIO] Failed to add APIC tag: {e}")
                    return
            audio.save()
        stats["audio_updated"] += 1
        filename = os.path.basename(path)
        logger.info(f"[AUDIO] Cover metadata fixed: {filename}")
    except Exception as e:
        logger.warning(f"[AUDIO] Failed to inject cover: {path} ({e})")

# ============================================================
# DIRECTORY PROCESSING
# ============================================================

def process_directory(path):
    start = time.time()
    logger.info(f"[DIR] Processing: {path}")

    audios = []
    cover_path = os.path.join(path, COVER_FILENAME)

    # Collect all audio files
    for f in os.listdir(path):
        full_path = Path(path) / f
        if full_path.suffix.lower() in SUPPORTED_AUDIO:
            audios.append(str(full_path))

    if not audios:
        logger.info(f"[DIR] No audio files found: {path}")
        folder_timings[path] = time.time() - start
        time.sleep(PAUSE_BETWEEN_DIRS)
        return

    # Get artist/album info for online search
    artist = album = None
    for audio in audios:
        try:
            if audio.endswith(".flac"):
                a = FLAC(audio)
                artist_list = a.get("artist")
                album_list = a.get("album")
                artist = artist_list[0] if artist_list else None
                album = album_list[0] if album_list else None
            elif audio.endswith(".mp3"):
                a = MP3(audio, ID3=ID3)
                if a.tags:
                    artist_tag = a.tags.get("TPE1")
                    album_tag = a.tags.get("TALB")
                    artist = artist_tag.text[0] if artist_tag else None
                    album = album_tag.text[0] if album_tag else None
            elif audio.endswith(".wav"):
                a = WAVE(audio)
                if a.tags:
                    artist_tag = a.tags.get("TPE1")
                    album_tag = a.tags.get("TALB")
                    artist = artist_tag.text[0] if artist_tag else None
                    album = album_tag.text[0] if album_tag else None
            if artist and album:
                break
        except Exception:
            continue

    final_cover = None
    cover_resized = False

    # 1. Check if cover.jpg exists in folder
    if os.path.exists(cover_path):
        try:
            with open(cover_path, "rb") as f:
                folder_cover = f.read()
            
            # Check size of cover.jpg
            img = Image.open(BytesIO(folder_cover))
            logger.info(f"[COVER] Found {COVER_FILENAME} with size {img.width}x{img.height}")
            
            if img.width > TARGET_SIZE[0] or img.height > TARGET_SIZE[1]:
                logger.info(f"[COVER] Resizing {COVER_FILENAME} from {img.width}x{img.height} to {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")
                final_cover, size = resize_image(folder_cover)
                
                # Replace the cover.jpg with resized version
                with open(cover_path, "wb") as f:
                    f.write(final_cover)
                logger.info(f"[COVER] Updated {COVER_FILENAME} to {size[0]}x{size[1]}")
                stats["covers_written"] += 1
                cover_resized = True
            else:
                logger.info(f"[COVER] {COVER_FILENAME} already optimized at {img.width}x{img.height}")
                final_cover = folder_cover
                
        except Exception as e:
            logger.warning(f"[COVER] Failed to process {COVER_FILENAME}: {e}")

    # 2. Check each audio file for oversized covers
    files_needing_update = []
    for audio in audios:
        current_cover = extract_audio_cover(audio)
        if current_cover:
            img = Image.open(BytesIO(current_cover))
            logger.info(f"[AUDIO] {os.path.basename(audio)} has cover {img.width}x{img.height}")
            
            if img.width > TARGET_SIZE[0] or img.height > TARGET_SIZE[1]:
                files_needing_update.append((audio, current_cover))
                logger.info(f"[AUDIO] {os.path.basename(audio)} needs cover update (oversized)")
        else:
            logger.info(f"[AUDIO] {os.path.basename(audio)} has no cover")
            files_needing_update.append((audio, None))

    # 3. If we have files needing updates but no cover.jpg, create one
    if files_needing_update and not final_cover:
        for audio, current_cover in files_needing_update:
            if current_cover:
                # Use the first available cover to create cover.jpg
                img = Image.open(BytesIO(current_cover))
                logger.info(f"[COVER] Creating {COVER_FILENAME} from {os.path.basename(audio)} ({img.width}x{img.height})")
                final_cover, size = resize_image(current_cover)
                with open(cover_path, "wb") as f:
                    f.write(final_cover)
                logger.info(f"[COVER] Created {COVER_FILENAME} ({size[0]}x{size[1]})")
                stats["covers_written"] += 1
                break

    # 4. If still no cover available, try online download
    if files_needing_update and not final_cover and is_online():
        logger.info(f"[COVER] No local covers available, searching online for {artist} / {album}")
        online = fetch_cover_online(artist, album)
        if online:
            final_cover, size = resize_image(online)
            with open(cover_path, "wb") as f:
                f.write(final_cover)
            logger.info(f"[COVER] Downloaded and created {COVER_FILENAME} ({size[0]}x{size[1]})")
            stats["covers_written"] += 1

    # 5. Update all files that need it
    if final_cover:
        for audio, current_cover in files_needing_update:
            inject_cover(audio, final_cover)
    else:
        if files_needing_update:
            logger.warning("[DIR] No cover available for updating audio files")

    # Log summary
    updated_count = len(files_needing_update) if final_cover else 0
    if updated_count > 0:
        logger.info(f"[DIR] Updated covers for {updated_count} audio files")
    elif files_needing_update:
        logger.info(f"[DIR] {len(files_needing_update)} files checked, no updates needed")
    else:
        logger.info(f"[DIR] All audio files already have properly sized covers")

    folder_timings[path] = time.time() - start
    time.sleep(PAUSE_BETWEEN_DIRS)

# ============================================================
# WALK
# ============================================================

def walk(root):
    for dirpath, _, _ in os.walk(root):
        process_directory(dirpath)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    logger.info("=== Starting cover processing ===")
    walk(os.getcwd())

    logger.info("=== Final report ===")
    for k, v in stats.items():
        logger.info(f"{k}: {v}")

    total = sum(folder_timings.values())
    logger.info(f"Directories processed: {len(folder_timings)}")
    logger.info(f"Total time: {total:.2f}s")
