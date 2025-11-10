import YTDlpWrap from 'yt-dlp-wrap';

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle OPTIONS request
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Get YouTube URL from query parameter
  const { url } = req.query;

  if (!url) {
    return res.status(400).json({
      error: 'Missing url parameter',
      usage: '/api/youtube-audio-url?url=YOUTUBE_URL'
    });
  }

  try {
    // Initialize yt-dlp
    const ytDlp = new YTDlpWrap();

    // Get video info and audio URL
    const info = await ytDlp.getVideoInfo([
      url,
      '--format', 'bestaudio',
      '--get-url',
      '--dump-json'
    ]);

    // Parse the JSON output
    const videoData = JSON.parse(info);

    // Extract audio URL (yt-dlp returns the direct URL)
    const audioUrl = videoData.url || videoData.requested_formats?.[0]?.url;

    if (!audioUrl) {
      throw new Error('Could not extract audio URL');
    }

    // Return the results
    return res.status(200).json({
      success: true,
      audioUrl: audioUrl,
      title: videoData.title,
      duration: videoData.duration,
      uploader: videoData.uploader
    });

  } catch (error) {
    return res.status(500).json({
      success: false,
      error: error.message
    });
  }
}