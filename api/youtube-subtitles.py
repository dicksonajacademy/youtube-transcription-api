from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
except ImportError:
    pass

class handler(BaseHTTPRequestHandler ):
    def do_GET(self):
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse URL parameters
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        video_id = params.get('videoId', [None])[0]
        
        if not video_id:
            self.wfile.write(json.dumps({
                'error': 'Missing videoId parameter',
                'usage': '/api/youtube-subtitles?videoId=VIDEO_ID'
            }).encode())
            return
        
        try:
            # Create API instance
            ytt_api = YouTubeTranscriptApi()
            
            # Fetch transcript (tries English first by default)
            fetched_transcript = ytt_api.fetch(video_id)
            
            # Convert snippets to plain text
            full_text = '\n'.join([snippet.text for snippet in fetched_transcript])
            
            # Return success with subtitle data
            self.wfile.write(json.dumps({
                'success': True,
                'hasSubtitles': True,
                'text': full_text,
                'language': fetched_transcript.language,
                'languageCode': fetched_transcript.language_code,
                'isGenerated': fetched_transcript.is_generated
            }).encode())
            
        except (TranscriptsDisabled, NoTranscriptFound):
            # No subtitles available
            self.wfile.write(json.dumps({
                'success': True,
                'hasSubtitles': False
            }).encode())
            
        except Exception as e:
            # Other errors
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())