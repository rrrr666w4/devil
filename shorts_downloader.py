import os
import yt_dlp
import glob
import json
from datetime import datetime

def create_session_folder():
    """Create a new folder for this session with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_folder = f"session_{timestamp}"
    os.makedirs(session_folder, exist_ok=True)
    print(f"📁 Session folder created: {session_folder}")
    return session_folder

def extract_hashtags_from_description(description):
    """Extract hashtags from video description"""
    if not description:
        return ""
    
    # Split description by lines and filter hashtags
    hashtags = []
    for line in description.split('\n'):
        words = line.split()
        for word in words:
            if word.startswith('#'):
                hashtags.append(word)
    
    return ' '.join(hashtags) if hashtags else description[:500]

def save_caption_with_hashtags(video_title, description, session_folder):
    """Save video caption and hashtags in separate file"""
    # Clean video title for filename
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_title = safe_title[:100]  # Limit filename length
    
    caption_file = os.path.join(session_folder, f"{safe_title}_caption.txt")
    
    # Extract hashtags
    hashtags = extract_hashtags_from_description(description)
    
    # Save caption and hashtags
    content = f"Title: {video_title}\n\n"
    content += f"Description:\n{description}\n\n"
    content += f"Hashtags:\n{hashtags}\n"
    
    try:
        with open(caption_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Saved caption: {safe_title}_caption.txt")
        return True
    except Exception as e:
        print(f"  ⚠️ Error saving caption for {safe_title}: {e}")
        return False

def finalize_metadata(session_folder):
    """Process and finalize metadata files in session folder"""
    print("\n⌒ Finalizing metadata files...")
    
    description_files = glob.glob(os.path.join(session_folder, "*.description"))
    
    for desc_file in description_files:
        try:
            with open(desc_file, 'r', encoding='utf-8') as f:
                description = f.read()
            
            # Get video title from filename
            base_name = os.path.splitext(os.path.basename(desc_file))[0]
            
            # Extract title (removing short_XX_ prefix)
            if base_name.startswith("short_"):
                video_title = base_name.split('_', 2)[2]
            else:
                video_title = base_name
            
            # Save as caption file
            save_caption_with_hashtags(video_title, description, session_folder)
            
            # Remove description file
            os.remove(desc_file)
            
        except Exception as e:
            print(f"  ⚠️ Error processing {desc_file}: {e}")

def run_shorts_downloader():
    """Main downloader function"""
    
    # Create session folder
    session_folder = create_session_folder()
    
    cookie_filename = 'cookies.txt'
    limit = 20
    
    print(f"🎬 Downloading up to {limit} trending Shorts to: {session_folder}\n")

    ydl_opts = {
        'format': 'bestvideo[height<=1080][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(session_folder, 'short_%(autonumber)02d_%(title).50s.%(ext)s'),
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
        'writeinfojson': True,
        'max_downloads': limit,
        'quiet': False,
        'no_warnings': False,
    }

    search_query = "ytsearch150:shorts india trending #viral"
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f'🔍 Searching: "{search_query}"\n')
            info = ydl.extract_info(search_query, download=True)
            
            # Process downloaded videos
            if info and 'entries' in info:
                for idx, entry in enumerate(info['entries'][:limit], 1):
                    if entry:
                        title = entry.get('title', f'video_{idx}')
                        description = entry.get('description', '')
                        
                        # Save caption with hashtags
                        save_caption_with_hashtags(title, description, session_folder)
                        print(f"  📹 Video {idx}: {title[:60]}")
            
        except Exception as e:
            print(f"\n⚠️ Note: Process completed or limited: {e}")
    
    # Finalize metadata files
    finalize_metadata(session_folder)
    
    # Summary
    video_count = len(glob.glob(os.path.join(session_folder, "short_*.mp4")))
    caption_count = len(glob.glob(os.path.join(session_folder, "*_caption.txt")))
    
    print(f"\n" + "="*50)
    print(f"✅ Session Complete!")
    print(f"📁 Folder: {session_folder}")
    print(f"🎬 Videos downloaded: {video_count}")
    print(f"📝 Captions saved: {caption_count}")
    print(f"="*50)

if __name__ == "__main__":
    run_shorts_downloader()
