import sys
import os
import yt_dlp
import ssl
import requests
from pytube import YouTube, Playlist
from pytube.innertube import InnerTube

# Set UTF-8 encoding for console output
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Monkey patch the requests session to disable SSL verification
InnerTube._default_clients = None
session = requests.Session()
session.verify = False
requests.packages.urllib3.disable_warnings()

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

def create_ssl_context():
    """Create a custom SSL context that's more permissive"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def download_with_pytube(url, output_path, stats):
    """Download video using pytube as a fallback"""
    try:
        # Create custom SSL context
        ssl_context = create_ssl_context()
        yt = YouTube(url, use_oauth=False, allow_oauth_cache=False)
        
        # Monkey patch the SSL context
        yt.stream_monostate._ssl_context = ssl_context
        
        video_id = yt.video_id
        video_title = yt.title
        
        if file_exists_in_directory(output_path, video_title):
            print(f"Video already exists: {video_title}")
            stats.add_skipped(video_id, "File already exists")
            return

        # Get the highest resolution stream that includes both video and audio
        stream = yt.streams.get_highest_resolution()
        
        # Download the video
        print(f"Downloading: {video_title}")
        stream.download(output_path=output_path)
        stats.add_success(video_id, video_title)
        print(f"Successfully downloaded: {video_title}")
        
    except Exception as e:
        stats.add_failure(url, f"Pytube error: {str(e)}")

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
                    print("Falling back to pytube...")
                    download_with_pytube(url, output_path, stats)
                    return

                video_id = info.get('id', 'NA')
                video_title = info.get('title', 'NA')
                
                if file_exists_in_directory(output_path, video_title):
                    print(f"Video already exists: {video_title}")
                    stats.add_skipped(video_id, "File already exists")
                    return

                # Download the video
                ydl.download([url])
                stats.add_success(video_id, video_title)
                
            except yt_dlp.utils.DownloadError as e:
                print(f"yt-dlp failed: {str(e)}")
                print("Falling back to pytube...")
                download_with_pytube(url, output_path, stats)
                
    except Exception as e:
        print(f"yt-dlp failed: {str(e)}")
        print("Falling back to pytube...")
        download_with_pytube(url, output_path, stats)

def process_url(url):
    print("YouTube Video/Playlist Downloader")
    print("=" * 33)

    try:
        # Create downloads directory if it doesn't exist
        downloads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
        os.makedirs(downloads_dir, exist_ok=True)

        # Initialize download stats
        stats = DownloadStats()

        # Check if it's a playlist
        if 'playlist' in url:
            try:
                print("Attempting to download playlist...")
                # Try using yt-dlp first
                try:
                    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
                        result = ydl.extract_info(url, download=False)
                        if result and 'entries' in result:
                            playlist_title = sanitize_filename(result.get('title', 'Playlist'))
                            playlist_dir = os.path.join(downloads_dir, playlist_title)
                            os.makedirs(playlist_dir, exist_ok=True)
                            
                            entries = list(result['entries'])
                            total_videos = len(entries)
                            print(f"\nDownloading playlist: {playlist_title}")
                            print(f"Found {total_videos} videos")
                            
                            for index, entry in enumerate(entries, 1):
                                if entry:
                                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                                    print(f"\nProcessing video {index}/{total_videos}")
                                    download_video(video_url, playlist_dir, stats)
                                else:
                                    print(f"Skipping video {index} - no information available")
                            
                            print(f"\nPlaylist download completed! Videos saved in: {playlist_dir}")
                            return
                except Exception as e:
                    print(f"yt-dlp failed: {str(e)}")
                    print("Trying pytube...")
                
                # Fallback to pytube
                playlist = Playlist(url)
                playlist_title = sanitize_filename(playlist.title)
                playlist_dir = os.path.join(downloads_dir, playlist_title)
                os.makedirs(playlist_dir, exist_ok=True)
                
                print(f"\nDownloading playlist: {playlist.title}")
                video_urls = playlist.video_urls
                total_videos = len(video_urls)
                print(f"Found {total_videos} videos in playlist")
                
                for index, video_url in enumerate(video_urls, 1):
                    print(f"\nProcessing video {index}/{total_videos}")
                    download_video(video_url, playlist_dir, stats)
                
                print(f"\nPlaylist download completed! Videos saved in: {playlist_dir}")
            except Exception as e:
                print(f"Error processing playlist: {str(e)}")
                stats.add_failure(url, f"Playlist processing error: {str(e)}")
        else:
            # Single video
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