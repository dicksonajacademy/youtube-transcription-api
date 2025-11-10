from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
except ImportError:
    # Will be installed by Vercel
    pass

class handler(BaseHTTPRequestHandler ):
    def do_GET(self):
        # Parse URL parameters
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)
        
        # Get video ID from query parameter
        video_id = params.get('videoId', [None])[0]
        
        if not video_id:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Missing videoId parameter',
                'usage': '/api/youtube-subtitles?videoId=VIDEO_ID'
            }).encode())
            return
        
        try:
            # Get list of available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to find best transcript (manual > auto-generated)
            best_transcript = None
            
            # First try manual transcripts
            try:
                best_transcript = transcript_list.find_manually_created_transcript(['en', 'zh-Hant', 'zh-Hans', 'zh'])
            except:
                pass
            
            # If no manual, try auto-generated
            if not best_transcript:
                try:
                    best_transcript = transcript_list.find_generated_transcript(['en', 'zh-Hant', 'zh-Hans', 'zh'])
                except:
                    pass
            
            # If found, fetch the transcript
            if best_transcript:
                fetched = best_transcript.fetch()
                
                # Convert to plain text
                full_text = '\n'.join([entry['text'] for entry in fetched])
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'hasSubtitles': True,
                    'language': best_transcript.language,
                    'languageCode': best_transcript.language_code,
                    'isGenerated': best_transcript.is_generated,
                    'text': full_text
                }).encode())
            else:
                # No subtitles found
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'hasSubtitles': False
                }).encode())
                
        except TranscriptsDisabled:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'hasSubtitles': False,
                'error': 'Transcripts are disabled for this video'
            }).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())