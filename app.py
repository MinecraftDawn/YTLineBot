from flask import Flask, request, abort , send_file

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
# Channel Secret
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    return send_file(app.root_path + "\\test.mp4",as_attachment=True)

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userID = event.source.user_id
    
#    ha = msg2yt(event.message.text)
    
    message = TextSendMessage(text=event.message.text)
    
    line_bot_api.reply_message(event.reply_token, message)
    
    video_message = VideoSendMessage(
            original_content_url='<Your_Ngrok_https>/download/filename',
            preview_image_url='https://i.vimeocdn.com/video/681613544_640.jpg'
        )
    line_bot_api.push_message(userID,video_message)
    
    """
    try:
        video_message = VideoSendMessage(
            original_content_url='https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
            preview_image_url='https://i.vimeocdn.com/video/681613544_640.jpg'
        )
        line_bot_api.push_message(userID,video_message)
    except linebot.exceptions.LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)
    """
from pytube import YouTube
def msg2yt(url):
    try:
        print(url)
        yt = YouTube(url)
        yt.streams.first().download(output_path='YT_Movies')
        return yt.title
    except:
        print("YT錯誤")
        return ""
    
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)