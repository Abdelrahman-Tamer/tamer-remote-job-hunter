import os
import sys
import time
import requests

BOT_TOKEN = "9027811700:AAEma9XxUdpK9xb324h3nba8TJ2jLT6r9nQ"
RESUMES_DIR = r"C:\Users\DELL\.gemini\antigravity\scratch\tamer_emam_resumes"
LATEST_MSG_FILE = os.path.join(RESUMES_DIR, "daily_job_reports", "latest_telegram_msg.txt")

# Permanent Telegram PDF file IDs
FILE_ID_CV_EN = "BQACAgQAAxkDAAMkavZLhtg7bYhwE-jn_ByqgneKb4oAAt8iAAKA-rBTgCyZrzO3n_E9BA"
FILE_ID_CV_AR = "BQACAgQAAxkDAAMlavZLhhq16LT8xf1tGy45EwXBx18AAuAiAAKA-rBTBMnEMVFMCKM9BA"

def send_message(chat_id, text, parse_mode="HTML"):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"Error sending msg: {e}")
        return False

def send_document(chat_id, file_id, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    payload = {"chat_id": chat_id, "document": file_id, "caption": caption}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending document: {e}")

def get_latest_jobs_report():
    if os.path.exists(LATEST_MSG_FILE):
        try:
            with open(LATEST_MSG_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return "⏳ جاري فحص وتحديث قائمة الوظائف الحية، أعد إرسال /jobs بعد لحظات..."

def handle_command(cmd, chat_id):
    cmd = cmd.strip().lower()
    print(f"Processing command '{cmd}' for chat_id {chat_id}")

    if cmd in ["/start", "/help"]:
        msg = """<b>مرحباً بك في بوت التوظيف الشخصي أ. تامر! ✈️</b>

البوت يعمل الآن ومستعد لتلقي أوامرك:
• <b>/jobs</b> : عرض أحدث وظائف الريموت الحقيقية الموثقة بروابط التقديم المباشرة.
• <b>/cv</b> : استلام نسختي السيرة الذاتية PDF (عربي وإنجليزي) فوراً في الشات.
• <b>/cover</b> : استلام رسالة التقديم (Cover Letter) الجاهزة للنسخ.
• <b>/gulf</b> : وظائف العمل عن بعد الموجهة لسوق الخليج.
"""
        send_message(chat_id, msg)

    elif cmd == "/cv":
        send_message(chat_id, "⏳ جاري إرسال نسختي السيرة الذاتية PDF فوراً...")
        send_document(chat_id, FILE_ID_CV_EN, "📄 Tamer Emam - English ATS Resume (PDF) | مخصصة للتقديم الدولي")
        send_document(chat_id, FILE_ID_CV_AR, "📄 تامر إمام - السيرة الذاتية باللغة العربية (PDF) | مخصصة لشركات الخليج")

    elif cmd in ["/jobs", "/gulf"]:
        jobs_text = get_latest_jobs_report()
        # Handle chunking if needed
        if len(jobs_text) <= 3800:
            send_message(chat_id, jobs_text)
        else:
            parts = jobs_text.split("───────────────────")
            chunk = ""
            for p in parts:
                p_clean = p.strip()
                if not p_clean:
                    continue
                addition = p_clean + "\n───────────────────\n"
                if len(chunk) + len(addition) > 3800:
                    send_message(chat_id, chunk.strip())
                    chunk = addition
                else:
                    chunk += addition
            if chunk:
                send_message(chat_id, chunk.strip())

    elif cmd == "/cover":
        pitch_text = """<b>نموذج رسالة التقديم السريعة (Copy & Paste):</b>

<code>Dear Hiring Manager,

With over 15 years of experience in hotel reservations management, direct property contracting with 4 & 5-star international chains (Marriott, Hilton, Four Seasons), and catering specifically to high-value GCC travelers across KSA and UAE, I am excited to apply for the Remote Travel / Reservations Specialist position.

I am available for immediate full-time remote engagement aligned with GCC working hours. Please find my attached ATS-optimized resume for your review.

Best regards,
Tamer Emam
Phone/WhatsApp: +20 100 471 3415
Email: tameremam123@gmail.com</code>
"""
        send_message(chat_id, pitch_text)
    else:
        send_message(chat_id, "عفواً، لم أتعرف على هذا الأمر. أرسل /help لعرض قائمة الأوامر المتاحة.")

def run_polling():
    print("Bot listener is running continuously in the background...")
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            r = requests.get(url, params={"offset": offset, "timeout": 15}, timeout=20)
            if r.status_code == 200:
                data = r.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "")
                    if chat_id and text.startswith("/"):
                        handle_command(text, chat_id)
            time.sleep(0.5)
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    run_polling()
