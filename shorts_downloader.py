import os
import yt_dlp
import glob

def finalize_metadata():
    """Ensures all .description files are renamed to _caption.txt"""
    print("\n⌒ Finalizing metadata files...")
    for desc_file in glob.glob("*.description"):
        base = os.path.splitext(desc_file)[0]
        target = base + "_caption.txt"
        if not os.path.exists(target):
            os.rename(desc_file, target)
            print(f"  ✅ Renamed metadata for: {os.path.basename(base)}")

def run_shorts_downloader():
    cookie_filename = 'cookies.txt'
    limit = 20
    existing_videos = glob.glob("short_*.mp4")
    print(f"ℹ Found {len(existing_videos)} existing downloads.")

    ydl_opts = {
        'format': 'bestvideo[height<=1080][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'short_%(autonumber)02d_%(title).50s.%(ext)s',
        'noplaylist': True,
        'ignoreerrors': True,
        'cookiefile': cookie_filename if os.path.exists(cookie_filename) else None,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash']
            }
        },
        'js_runtimes': {'deno': {}},
        'sleep_interval': 3,
        'max_sleep_interval': 7,
        'match_filter': yt_dlp.utils.match_filter_func("duration < 61 & duration > 5"),
        'writedescription': True,
        'max_downloads': limit,
    }

    search_query = "ytsearch150:shorts india trending #viral"
    print(f'ထဠ Searching and downloading up to {limit} trending Shorts...')
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([search_query])
        except Exception as e:
            print(f"\n☐ Note: Process stopped or limited: {e}")
    finalize_metadata()

if __name__ == "__main__":
    run_shorts_downloader()
