import sys
import os
import yt_dlp

# Set UTF-8 encoding for console output
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Set path to ffmpeg
FFMPEG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg', 'ffmpeg-master-latest-win64-gpl', 'bin', 'ffmpeg.exe')

class DownloadStats:
    def __init__(self):
        self.successful = []
        self.failed = []
        self.skipped = []

    def add_success(self, video_id, title):
        self.successful.append((video_id, title))

    def add_failure(self, video_id, error):
        self.failed.append((video_id, error))

    def add_skipped(self, video_id, reason):
        self.skipped.append((video_id, reason))

    def print_summary(self):
        print("\nDownload Summary")
        print("=" * 50)
        print(f"Total successful downloads: {len(self.successful)}")
        print(f"Total failed downloads: {len(self.failed)}")
        print(f"Total skipped downloads: {len(self.skipped)}")
        
        if self.failed:
            print("\nFailed Downloads:")
            for video_id, error in self.failed:
                print(f"- Video {video_id}: {error}")
        
        if self.skipped:
            print("\nSkipped Downloads:")
            for video_id, reason in self.skipped:
                print(f"- Video {video_id}: {reason}")

def sanitize_filename(title):
    """Sanitize the filename to match YouTube's filename sanitization"""
    if not isinstance(title, str):
        title = str(title)
    
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, '_')
    # Replace spaces with underscores
    title = title.replace(' ', '_')
    # Handle unicode characters
    title = title.encode('utf-8', 'ignore').decode('utf-8')
    return title

def file_exists_in_directory(directory, video_title):
    """Check if a video file exists in the directory, using flexible matching"""
    try:
        # Sanitize the video title
        sanitized_title = sanitize_filename(video_title)
        
        # Check for common variations of the filename
        possible_names = [
            f"{video_title}.mp4",
            f"{sanitized_title}.mp4",
            f"{video_title}.mkv",
            f"{sanitized_title}.mkv"
        ]
        
        # Check if any variation exists
        for filename in os.listdir(directory):
            try:
                filename_lower = filename.lower()
                for possible_name in possible_names:
                    if filename_lower == possible_name.lower():
                        return True
                    # Also check if the video ID is in the filename (common in playlist downloads)
                    if video_title.lower() in filename_lower and filename_lower.endswith('.mp4'):
                        return True
            except UnicodeEncodeError:
                continue
        return False
    except Exception as e:
        print(f"Warning: Error checking file existence: {str(e)}")
        return False

def download_video(url, output_path, stats):
    try:
        ydl_opts = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': False,
            'extract_flat': False,
            'socket_timeout': 30,
            'retries': 3
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    stats.add_failure(url, "Video information could not be extracted")
                    return

                video_id = info.get('id', 'NA')
                video_title = info.get('title', 'NA')
                
                # Check if file already exists using the improved function
                if file_exists_in_directory(output_path, video_title):
                    print(f"Video already exists: {video_title}")
                    stats.add_skipped(video_id, "File already exists")
                    return

                # Download the video
                ydl.download([url])
                stats.add_success(video_id, video_title)
                
            except yt_dlp.utils.DownloadError as e:
                error_message = str(e)
                if "Video unavailable" in error_message:
                    stats.add_failure(url, "Video unavailable")
                else:
                    stats.add_failure(url, f"Download error: {error_message}")
                
    except Exception as e:
        stats.add_failure(url, f"Unexpected error: {str(e)}")

def process_url(url):
    print("YouTube Video/Playlist Downloader")
    print("=" * 33)

    try:
        # Create downloads directory if it doesn't exist
        downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        os.makedirs(downloads_dir, exist_ok=True)

        # Initialize download stats
        stats = DownloadStats()

        with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            result = ydl.extract_info(url, download=False)
            
            if result is None:
                print("Error: Could not extract video/playlist information")
                return

            if 'entries' in result:  # It's a playlist
                print("Detected playlist URL")
                print("Fetching playlist information...")
                
                playlist_title = result.get('title', 'Playlist')
                playlist_dir = os.path.join(downloads_dir, playlist_title)
                os.makedirs(playlist_dir, exist_ok=True)
                
                entries = list(result['entries'])
                total_videos = len(entries)
                print(f"\nDownloading playlist: {playlist_title}")
                
                for index, entry in enumerate(entries, 1):
                    if entry:
                        video_url = entry['url']
                        print(f"\nProcessing video {index}/{total_videos}")
                        download_video(video_url, playlist_dir, stats)
                    else:
                        stats.add_failure(f"Video #{index}", "Entry information missing")
                
                print(f"\nPlaylist download completed! Videos saved in: {playlist_dir}")
                
            else:  # Single video
                print("Detected single video URL")
                download_video(url, downloads_dir, stats)
                print(f"\nVideo download completed! Video saved in: {downloads_dir}")

            # Print download statistics
            stats.print_summary()

    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Please provide a YouTube URL as argument")
        print("Usage: python youtube_downloader.py <youtube_url>")
        sys.exit(1)
        
    url = sys.argv[1]
    process_url(url)

if __name__ == "__main__":
    main()