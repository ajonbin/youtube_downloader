# YouTube Video Downloader

A Python script to download YouTube videos and playlists in high quality using yt-dlp.

## Features

- Download single videos or entire playlists
- Automatic best quality selection (up to 1080p)
- Smart file existence checking to avoid duplicate downloads
- Support for Unicode characters in video titles
- Detailed progress tracking and download statistics
- Proper error handling for unavailable videos
- Automatic merging of video and audio streams

## Requirements

- Python 3.6 or higher
- FFmpeg (included in the repository)
- Required Python packages (install via pip):
  ```
  pip install -r requirements.txt
  ```

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd youtube_downloader
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. FFmpeg is included in the repository under the `ffmpeg` directory, no additional installation needed.

## Usage

1. Download a single video:
   ```
   python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID
   ```

2. Download an entire playlist:
   ```
   python youtube_downloader.py https://www.youtube.com/playlist?list=PLAYLIST_ID
   ```

The script will:
- Create a `downloads` directory if it doesn't exist
- Create a playlist-specific directory for playlist downloads
- Skip any videos that have already been downloaded
- Show progress for each video download
- Provide a summary of successful, failed, and skipped downloads

## Features in Detail

### Smart File Existence Checking
- Checks for existing files before downloading
- Handles different filename formats and character encodings
- Supports multiple video formats (mp4, mkv)
- Recognizes playlist-specific naming patterns

### Progress Tracking
- Real-time download progress for each video
- Overall playlist progress
- Detailed summary after completion showing:
  - Total successful downloads
  - Total failed downloads
  - Total skipped downloads
  - List of skipped videos with reasons

### Error Handling
- Graceful handling of unavailable videos
- Network error recovery with retries
- Unicode character support in filenames
- File system operation error handling

## Output Format

Videos are saved in the following structure:
```
downloads/
├── single_videos/
│   └── video_title.mp4
└── playlist_name/
    ├── video1_title.mp4
    ├── video2_title.mp4
    └── ...
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
