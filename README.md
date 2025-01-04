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
   ```bash
   git clone https://github.com/ajonbin/youtube_downloader.git
   cd youtube_downloader
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   .\venv\Scripts\activate  # On Windows
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Download a single video:
   ```bash
   python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID
   ```

2. Download an entire playlist:
   ```bash
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

## Troubleshooting

### SSL Issues
If you encounter SSL errors like:
```
[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1007)
```

This can happen due to:
- Network instability
- Proxy interference
- SSL certificate verification issues
- Server-side connection limits

The script handles these issues automatically through:
1. Multiple retry attempts
2. Fallback to alternative download methods
3. Custom SSL context handling
4. Automatic recovery mechanisms

If you still experience issues, you can try:
1. Check your network connection
2. Configure your proxy settings if using one
3. Update your SSL certificates
4. Try downloading with a different network connection

### Common Issues

1. **Video Unavailable**
   - The video might be private or deleted
   - Region restrictions might apply
   - Try using a VPN if region-restricted

2. **Download Speed Issues**
   - Check your internet connection
   - Try during off-peak hours
   - Consider using a different network

3. **File Format Issues**
   - The script automatically handles format conversion
   - FFmpeg is required for some conversions
   - Check if FFmpeg is properly installed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
