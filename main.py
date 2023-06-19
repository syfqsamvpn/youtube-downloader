from flask import Flask, request, send_file
import os
import pytube
from pytube.exceptions import RegexMatchError

app = Flask(__name__)

def sanitize_file_name(file_name):
    valid_symbols = ['.', '_', '-', '(', ')']
    return ''.join(c if c.isalnum() or c in valid_symbols else '.' if c == ' ' else '' for c in file_name)

@app.route('/', methods=['GET', 'POST'])
def download_youtube_media():
    if request.method == 'POST':
        url = request.form.get('url')
        media_type = request.form.get('media_type')

        try:
            youtube = pytube.YouTube(url)
            youtube_title = youtube.title
            sanitized_title = sanitize_file_name(youtube_title)

            if media_type == 'mp3':
                audio_streams = youtube.streams.filter(only_audio=True).order_by('abr').desc()
                highest_quality_audio = audio_streams.first()

                folder_mp3 = 'mp3_files'
                if not os.path.exists(folder_mp3):
                    os.makedirs(folder_mp3)
                audio_path = os.path.join(folder_mp3, sanitized_title + '.mp3')
                sanitized_title = sanitized_title + '.mp3'

                highest_quality_audio.download(output_path=folder_mp3, filename=sanitized_title)
                return send_file(audio_path, as_attachment=True)

            elif media_type == 'mp4':
                highest_quality_video = youtube.streams.get_highest_resolution()

                folder_mp4 = 'mp4_files'
                if not os.path.exists(folder_mp4):
                    os.makedirs(folder_mp4)
                video_path = os.path.join(folder_mp4, sanitized_title + '.mp4')
                sanitized_title = sanitized_title + '.mp4'

                highest_quality_video.download(output_path=folder_mp4, filename=sanitized_title)
                return send_file(video_path, as_attachment=True)
            
            else:
                return "Invalid media type. Please select 'mp3' or 'mp4'."

        except RegexMatchError:
            return "Invalid YouTube URL."

    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>YouTube Media Downloader</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <style>
                body {
                    padding: 20px;
                    background-color: #1a1a1a;
                    color: #ffffff;
                }

                .container {
                    max-width: 600px;
                    margin: 0 auto;
                }

                h1 {
                    color: #ffffff;
                }

                .form-control {
                    color: #ffffff;
                }

                .btn-primary {
                    background-color: #428bca;
                    border-color: #428bca;
                }

                .btn-primary:hover {
                    background-color: #3071a9;
                    border-color: #285e8e;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>YouTube Media Downloader</h1>
                <form method="POST">
                    <div class="mb-3">
                        <input type="text" class="form-control" name="url" placeholder="Enter YouTube video URL" required>
                    </div>
                    <div class="mb-3">
                        <label for="media_type" class="form-label">Select media type:</label>
                        <select name="media_type" class="form-control">
                            <option value="mp3">MP3</option>
                            <option value="mp4">MP4</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Download</button>
                </form>
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
