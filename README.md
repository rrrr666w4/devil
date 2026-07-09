# 🎥 YouTube Shorts Downloader Bot

Automatically download YouTube Shorts with metadata, captions, and hashtags!

## 📋 Features

✅ **Automated Downloads** - GitHub Actions workflow runs daily  
✅ **Metadata Storage** - Videos, captions, and JSON metadata saved in repo  
✅ **Hashtag Extraction** - Automatically extracts hashtags from descriptions  
✅ **Organized Structure** - Session-based folder organization with timestamps  
✅ **Index File** - JSON index for easy browsing and downloading  

## 📁 Folder Structure

```
downloads/
├── session_20260709_083120/
│   ├── short_00_shorts_india_trending_viral.mp4
│   ├── short_00_shorts_india_trending_viral.info.json
│   ├── short_00_shorts_india_trending_viral_caption.txt
│   ├── short_01_...
│   └── INDEX.json  (Master index for all videos in session)
├── session_20260710_000000/
│   └── ...
```

## 📖 Using the INDEX.json File

Each session folder contains an `INDEX.json` file with:
- Video filename and path
- Caption content
- Metadata file links
- Session timestamp and video count

**Example:**
```json
{
  "session": "session_20260709_083120",
  "created_at": "2026-07-09T08:31:20.000000",
  "total_videos": 5,
  "videos": [
    {
      "filename": "short_00_video_title.mp4",
      "video_file": "downloads/session_20260709_083120/short_00_video_title.mp4",
      "caption_file": "downloads/session_20260709_083120/video_title_caption.txt",
      "metadata_file": "downloads/session_20260709_083120/short_00_video_title.info.json",
      "caption_content": "Title: ...\nDescription: ...\nHashtags: #shorts #trending"
    }
  ]
}
```

## 🚀 How to Download Videos

### Option 1: Download from GitHub Web UI
1. Go to the `downloads/session_XXXXXXX/` folder
2. Click on any `.mp4` file
3. Click the download icon (⬇️)

### Option 2: Clone & Download Everything
```bash
git clone https://github.com/rrrr666w4/devil.git
cd devil
```

### Option 3: Using INDEX.json to Find Videos
```bash
# Read the index to see all videos in a session
cat downloads/session_20260709_083120/INDEX.json | jq '.videos[].filename'
```

## ⚙️ How It Works

1. **Trigger**: Daily at midnight UTC (or manual trigger)
2. **Download**: Searches and downloads up to 20 trending shorts
3. **Process**: Extracts metadata, captions, and hashtags
4. **Store**: Saves in organized session folder
5. **Index**: Creates INDEX.json for easy navigation
6. **Commit**: Auto-commits to repo (no manual action needed!)

## 🔍 Search Query

Currently searches: `ytsearch:shorts india trending viral`

To change, edit line 110 in `shorts_downloader.py`:
```python
search_query = "ytsearch:your_search_here"
```

## 📝 File Types Saved

- **`.mp4`** - Video file
- **`.info.json`** - Full metadata from yt-dlp
- **`_caption.txt`** - Title, description, and extracted hashtags
- **`INDEX.json`** - Session index with all video references

## 🔧 Requirements

- Python 3.11+
- yt-dlp
- GitHub Actions (automatic)

## 📊 Stats from Last Run

Check the workflow run logs for:
- ✅ Total videos downloaded
- ✅ Captions processed
- ✅ Index file generated

---

**Created with ❤️ by YouTube Shorts Bot**
