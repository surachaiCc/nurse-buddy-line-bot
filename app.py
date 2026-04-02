from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import google.generativeai as genai
import os

app = Flask(__name__)

# --- LINE Configuration (ข้อมูลของเช่ง) ---
LINE_CHANNEL_ACCESS_TOKEN = 'Jr8sN2y9ZSF8EUSTHDMwSwudlp9Xi8Jgc66Wte89Fqk/v+IjqYC+MRkGt3cHB4cpYuhdklqCKZwHJGb0tNeX0qe/I7YrXADRPUhb2tZ/6dgAGCxkXVCbwAxMIu0rzUtYhgitSd/w5q04nSMezIvPWAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '8cb32016f22c1414bbd599c6ccbb1219'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# --- Gemini Configuration (ข้อมูลของเช่ง) ---
genai.configure(api_key="AIzaSyAPWqOMXrrNq34NB_1tn1Sapl2LojC3qu0")

# --- ปรับแต่งบุคลิกบอทตรงนี้ (System Instruction) ---
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="""
    คุณชื่อ 'Nurse Buddy' เป็นพยาบาลอัจฉริยะและผู้ช่วยส่วนตัวของคุณหมอเช่ง
    บุคลิก: ใจดี, รอบรู้เรื่องสุขภาพ, พูดจาสุภาพแต่กระชับตรงประเด็น
    หน้าที่: ตอบคำถามสุขภาพเบื้องต้น, ให้กำลังใจคนไข้, และช่วยคุณหมอเช่งจดบันทึก
    ข้อห้าม: ห้ามวินิจฉัยโรคเองแบบฟันธง ให้เน้นแนะนำให้ปรึกษาแพทย์หากมีอาการรุนแรง
    """
)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # รับข้อความจาก LINE แล้วส่งให้ Gemini
    user_message = event.message.text
    response = model.generate_content(user_message)
    
    # ส่งคำตอบกลับไปที่ LINE
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response.text)
    )

if __name__ == "__main__":
    app.run(port=5000)
