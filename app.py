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

# 監聽目標為 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # 取得 X-Line-Signature 的標頭值
    signature = request.headers['X-Line-Signature']
    # 以文字方式取得request body
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # 處理webhook主體
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 監聽目標為 /download/<filename> 的 GET Request
@app.route("/download/<filename>", methods=['GET'])
def download_file(filename):
    
	# 設定影片目錄
    urlPath = app.root_path + '\\YT_Movies\\' + filename
    # 判斷檔案是否存在
    if os.path.exists(urlPath):
		# 送出影片
        return send_file(urlPath,as_attachment=True)
    else:
        return "檔案不存在" + urlPath

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	# 取得使用者的user_id
    userID = event.source.user_id
    # 取得使用者發出的訊息
    message = TextSendMessage(text=event.message.text)
    # 回復與使用者傳送相同的訊息
    line_bot_api.reply_message(event.reply_token, message) 
    # 取得YT影片網址取hash後的字串
    hashName = msg2yt(event.message.text)
    
    # 包裝影片網址及影片縮圖網址
    video_message = VideoSendMessage(
            original_content_url='https://<Your_Ngrok_Url>/download/' + str(hashName) + '.mp4',
            preview_image_url='https://<Your_Ngrok_Url>/download/' + str(hashName) + '.png'
        )
    line_bot_api.push_message(userID,video_message)
    
from pytube import YouTube
import requests

def msg2yt(url):
#try:
	# 設定YT物件
    yt = YouTube(url)
	# 對影片標題取hash並轉成字串
    fileName = str(hash(yt.title))
	# 下載影片，並設定目錄及名稱
    yt.streams.first().download(output_path='YT_Movies',filename=fileName)
    # 取得影片縮圖網址
    image = requests.get(yt.thumbnail_url)
    # 若縮圖網址成功則繼續
    if image.status_code == 200:
		# 開啟檔案並寫入
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