import os
import sys
import yt_dlp
import glob
import json
from datetime import datetime
import time

def create_session_folder():
    """Create a new folder for this session with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_folder = f"downloads/session_{timestamp}"
    os.makedirs(session_folder, exist_ok=True)
    print(f"📁 Session folder created: {session_folder}")
    return session_folder

def extract_hashtags_from_description(description):
    """Extract hashtags from video description"""
    if not description:
        return ""

    hashtags = []
    for line in description.split('\n'):
        words = line.split()
        for word in words:
            if word.startswith('#'):
                hashtags.append(word)

    return ' '.join(hashtags) if hashtags else description[:500]

def save_caption_with_hashtags(video_title, description, session_folder):
    """Save video caption and hashtags in separate file"""
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title[:100]

    caption_file = os.path.join(session_folder, f"{safe_title}_caption.txt")

    hashtags = extract_hashtags_from_description(description)

    content = f"Title: {video_title}\n\n"
    content += f"Description:\n{description}\n\n"
    content += f"Hashtags:\n{hashtags}\n"

    try:
        with open(caption_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Saved caption: {safe_title}_caption.txt")
        return True
    except Exception as e:
        print(f"  ⚠️ Error saving caption: {e}")
        return False

def create_index_file(session_folder):
    """Create an index file with download links and metadata"""
    videos = sorted(glob.glob(os.path.join(session_folder, "short_*.mp4")))

    index = {
        "session": os.path.basename(session_folder),
        "created_at": datetime.now().isoformat(),
        "total_videos": len(videos),
        "videos": []
    }

    for video in videos:
        base_name = os.path.basename(video)
        video_name = base_name.replace('short_', '').replace('.mp4', '')

        info_json = os.path.join(session_folder, f"{base_name.replace('.mp4', '.info.json')}")
        caption_file = os.path.join(session_folder, f"{video_name}_caption.txt")

        video_info = {
            "filename": base_name,
            "video_file": f"downloads/{os.path.relpath(video)}",
            "caption_file": f"downloads/{os.path.relpath(caption_file)}" if os.path.exists(caption_file) else None,
            "metadata_file": f"downloads/{os.path.relpath(info_json)}" if os.path.exists(info_json) else None
        }

        # Add caption content if available
        if os.path.exists(caption_file):
            try:
                with open(caption_file, 'r', encoding='utf-8') as f:
                    video_info["caption_content"] = f.read()
            except Exception:
                pass

        index["videos"].append(video_info)

    index_file = os.path.join(session_folder, "INDEX.json")
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"  📋 Index file created: INDEX.json")
    return index_file

def finalize_metadata(session_folder):
    """Process and finalize metadata files"""
    print("\n⚒️ Finalizing metadata files...")

    description_files = glob.glob(os.path.join(session_folder, "*.description"))

    for desc_file in description_files:
        try:
            with open(desc_file, 'r', encoding='utf-8') as f:
                description = f.read()

            base_name = os.path.splitext(os.path.basename(desc_file))[0]

            if base_name.startswith("short_"):
                video_title = base_name.split('_', 2)[2]
            else:
                video_title = base_name

            save_caption_with_hashtags(video_title, description, session_folder)
            os.remove(desc_file)

        except Exception as e:
            print(f"  ⚠️ Error processing metadata: {e}")

    # Create index file
    create_index_file(session_folder)

def run_shorts_downloader():
    """Main downloader function with better error handling"""

    session_folder = create_session_folder()
    limit = 20

    print(f"🎬 Downloading up to {limit} trending Shorts\n")

    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'outtmpl': os.path.join(session_folder, 'short_%(autonumber)02d_%(title).50s.%(ext)s'),
        'noplaylist': True,
        'ignoreerrors': True,
        'socket_timeout': 30,
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'android'],
                'skip': ['hls', 'dash']
            }
        },
        'sleep_interval': 2,
        'max_sleep_interval': 5,
        'match_filter': yt_dlp.utils.match_filter_func("duration < 61 & duration > 5"),
        'writedescription': True,
        'writeinfojson': True,
        'writesubtitles': False,
        'max_downloads': limit,
        'quiet': False,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    }

    # Use cookies.txt to avoid YouTube's "confirm you're not a bot" block on
    # GitHub Actions' shared IPs. Without this, extract_info was failing
    # almost instantly and the broad except below silently swallowed it.
    cookies_path = 'cookies.txt'
    if os.path.exists(cookies_path) and os.path.getsize(cookies_path) > 0:
        ydl_opts['cookiefile'] = cookies_path
        print(f"🍪 Using cookies file: {cookies_path}")
    else:
        print(f"⚠️ No cookies.txt found (or it's empty) — YouTube may block this run as a bot.")

    # "ytsearch:" alone only returns 1 result. "ytsearchN:" tells yt-dlp how
    # many results to pull — we search a bit wider than `limit` since some
    # results will get filtered out by duration/match_filter below.
    search_query = f"ytsearch{limit * 3}:shorts india trending viral"
    download_failed = False

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f'🔍 Searching: "{search_query}"\n')
            info = ydl.extract_info(search_query, download=True)

            if info and 'entries' in info:
                for idx, entry in enumerate(info['entries'][:limit], 1):
                    if entry:
                        title = entry.get('title', f'video_{idx}')
                        description = entry.get('description', '')
                        save_caption_with_hashtags(title, description, session_folder)
                        print(f"  📹 Video {idx}: {title[:60]}")
                        time.sleep(1)

        except Exception as e:
            print(f"\n⚠️ Process error: {e}")
            download_failed = True

    finalize_metadata(session_folder)

    video_count = len(glob.glob(os.path.join(session_folder, "short_*.mp4")))
    caption_count = len(glob.glob(os.path.join(session_folder, "*_caption.txt")))

    print(f"\n" + "="*50)
    print(f"✅ Session Complete!")
    print(f"📁 Folder: {session_folder}")
    print(f"🎬 Videos: {video_count}")
    print(f"📝 Captions: {caption_count}")
    print(f"📋 Index: {os.path.join(session_folder, 'INDEX.json')}")
    print(f"="*50)

    # Previously the workflow always showed green even when nothing was
    # downloaded. Now we fail loudly so GitHub Actions actually reflects
    # what happened.
    if video_count == 0:
        print("\n❌ No videos were downloaded this run. Failing the job so it's visible in Actions.")
        sys.exit(1)

    if download_failed:
        print("\n⚠️ Some videos downloaded, but an error also occurred mid-run. Check logs above.")

    return session_folder

if __name__ == "__main__":
    run_shorts_downloader()
