from flask import Flask, request, abort , send_file

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import os

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
    
    urlPath = app.root_path + '\\YT_Movies\\' + filename
    #判斷檔案是否存在
    if os.path.exists(urlPath):
        return send_file(urlPath,as_attachment=True)
    else:
        return "檔案不存在" + urlPath

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userID = event.source.user_id
    
    message = TextSendMessage(text=event.message.text)
    
    line_bot_api.reply_message(event.reply_token, message) 
    
    hashName = msg2yt(event.message.text)
    
    
    video_message = VideoSendMessage(
            original_content_url='https://<Your_Ngrok_Url>/download/' + str(hashName) + '.mp4',
            preview_image_url='https://<Your_Ngrok_Url>/download/' + str(hashName) + '.png'
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
import requests

def msg2yt(url):
#try:
    print(url)
    yt = YouTube(url)
    print(str(hash(yt.title)))
    fileName = str(hash(yt.title))
    yt.streams.first().download(output_path='YT_Movies',filename=fileName)
    
    image = requests.get(yt.thumbnail_url)
    
    if image.status_code == 200:
        with open(app.root_path + "\\YT_Movies\\" + fileName + ".png", 'wb') as f:
            f.write(image.content)
            f.close()
    else:
        print("Error")
    del image
    
    return fileName

#except:
    print("YT錯誤")
    return ""
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)