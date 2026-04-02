import os, sys
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai

app = Flask(__name__)

# --- CONFIG (เช็คดีๆ ว่าก๊อปมาครบนะ) ---
LINE_TOKEN = 'Jr8sN2y9ZSF8EUSTHDMwSwudlp9Xi8Jgc66Wte89Fqk/v+IjqYC+MRkGt3cHB4cpYuhdklqCKZwHJGb0tNeX0qe/I7YrXADRPUhb2tZ/6dgAGCxkXVCbwAxMIu0rzUtYhgitSd/w5q04nSMezIvPWAdB04t89/1O/w1cDnyilFU='
LINE_SECRET = '8cb32016f22c1414bbd599c6ccbb1219'
GEMINI_KEY = 'AIzaSyAPWqOMXrrNq34NB_1tn1Sapl2LojC3qu0'

line_bot_api = LineBotApi(LINE_TOKEN)
handler = WebhookHandler(LINE_SECRET)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route("/")
def home():
    return "Nurse Buddy is Online!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    print(">>> มีสัญญาณเข้าที่ /callback แล้ว!") # เช็กว่า LINE ส่งมาถึงมั้ย
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(">>> Error: ลายเซ็นผิด (Channel Secret อาจจะไม่ตรง)")
        abort(400)
    except Exception as e:
        print(f">>> Error อื่นๆ: {e}")
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    print(f">>> คุณหมอเช่งพิมพ์มาว่า: {user_text}")
    
    try:
        print(">>> กำลังถาม Gemini...")
        response = model.generate_content(user_text)
        reply_text = response.text
        print(f">>> Gemini ตอบว่า: {reply_text}")
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        print(">>> ส่งข้อความกลับไปที่ LINE เรียบร้อย!")
    except Exception as e:
        print(f">>> พังตอนตอบ: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ระบบขัดข้องนิดหน่อยค่ะคุณหมอ"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
