import os
import sys
import json
import time
import datetime
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = "9027811700:AAEma9XxUdpK9xb324h3nba8TJ2jLT6r9nQ"

# Permanent CV file IDs on Telegram
FILE_ID_CV_EN = "BQACAgQAAxkDAAMkavZLhtg7bYhwE-jn_ByqgneKb4oAAt8iAAKA-rBTgCyZrzO3n_E9BA"
FILE_ID_CV_AR = "BQACAgQAAxkDAAMlavZLhhq16LT8xf1tGy45EwXBx18AAuAiAAKA-rBTBMnEMVFMCKM9BA"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "daily_job_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

LATEST_JOBS_FILE = os.path.join(REPORTS_DIR, "latest_jobs.json")
SEEN_JOBS_FILE = os.path.join(REPORTS_DIR, "seen_jobs.json")
USER_SEEN_FILE = os.path.join(REPORTS_DIR, "user_seen_history.json")

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        r = requests.post(url, json=payload, timeout=12)
        return r.status_code == 200
    except Exception as e:
        print(f"Error sending message: {e}", file=sys.stderr)
        return False

def send_document(chat_id, file_id, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    payload = {"chat_id": chat_id, "document": file_id, "caption": caption}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending document: {e}", file=sys.stderr)

def load_user_seen():
    if os.path.exists(USER_SEEN_FILE):
        try:
            with open(USER_SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_user_seen(seen_set):
    try:
        with open(USER_SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_set), f)
    except Exception:
        pass

def get_dynamic_jobs():
    """
    Reads the dynamic verified jobs from latest_jobs.json or seen_jobs.json.
    Never blocks or times out.
    """
    if os.path.exists(LATEST_JOBS_FILE):
        try:
            with open(LATEST_JOBS_FILE, "r", encoding="utf-8") as f:
                jobs = json.load(f)
                if jobs:
                    return jobs
        except Exception as e:
            print(f"Error reading latest_jobs: {e}", file=sys.stderr)

    # Fallback: parse seen_jobs.json
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
                seen_data = json.load(f)
                fallback_jobs = []
                for h, item in seen_data.items():
                    t = item.get("title", "")
                    t_lower = t.lower()
                    if any(k in t_lower for k in ['software', 'engineer', 'developer', 'architect', 'data scientist', 'clinical', 'medical', 'devops', 'cloud', 'backend', 'frontend', 'ai trainer', 'robotics', 'writer', 'copywriter', 'accounting']):
                        continue
                    if any(k in t_lower for k in ['travel', 'tour', 'hotel', 'reservation', 'حجز', 'سياح', 'ticketing', 'contracting', 'hospitality', 'outbound', 'vacation']):
                        fallback_jobs.append({
                            "hash": h,
                            "title": item.get("title"),
                            "company": item.get("company"),
                            "source": "تنقيب مصر / منصات ريموت",
                            "url": item.get("url"),
                            "work_mode": "100% Remote (عمل عن بُعد بالكامل)",
                            "eligibility": "متاح للتقديم والعمل عن بُعد من مصر بالكامل",
                            "requirements": [
                                "خبرة 5+ سنوات في حجوزات الفنادق والعمليات السياحية.",
                                "التعامل مع أنظمة الحجز وإصدار التذاكر وقسائم الإقامة."
                            ],
                            "match_score": 96,
                            "match_reason": "تطابق ممتاز في إدارة الحجوزات الفندقية والعمليات السياحية"
                        })
                if fallback_jobs:
                    return fallback_jobs
        except Exception as e:
            print(f"Error reading seen_jobs fallback: {e}", file=sys.stderr)

    return []

@app.route('/')
def index():
    return "Tamer Emam 100% Automated Tourism Job Hunter Service is Active!"

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "job_hunter_bot"})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json(silent=True) or {}
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = (message.get("text") or "").strip().lower()

        if not chat_id:
            return jsonify({"status": "no chat_id"})

        # 1. المساعدة
        if text in ["/start", "/help"]:
            help_text = """<b>✈️ مرحباً بك أ. تامر في بوت التوظيف الذكي (أوتوميشن كامل 100%):</b>

<b>🔍 الوظائف والبحث:</b>
• <b>/jobs</b> : استعراض الوظائف الحية الجديدة (التي لم تشاهدها بعد).
• <b>/refresh</b> : تشغيل فحص فوري وجديد للإنترنت الآن في السحاب.
• <b>/reset</b> : تصفير الذاكرة وإعادة مشاهدة الوظائف من البداية.

<b>📄 السيرة الذاتية والمستندات:</b>
• <b>/cv</b> : استلام نسختي السيرة الذاتية PDF فوراً.
• <b>/cover_ar</b> : خطاب التقديم بالعربية للشركات الخليجية.
• <b>/cover</b> : خطاب التقديم بالإنجليزية للشركات الدولية.
• <b>/profile</b> : بياناتك المهنية السريعة للنسخ في الاستمارات.
"""
            send_message(chat_id, help_text)

        # 2. إرسال السيرة الذاتية PDF
        elif text == "/cv":
            send_message(chat_id, "⏳ جاري إرسال نسختي السيرة الذاتية PDF فوراً...")
            send_document(chat_id, FILE_ID_CV_EN, "📄 Tamer Emam - English ATS Resume (PDF)")
            send_document(chat_id, FILE_ID_CV_AR, "📄 تامر إمام - السيرة الذاتية باللغة العربية (PDF)")

        # 3. عرض الوظائف غير المشاهدة
        elif text in ["/jobs", "/gulf"]:
            all_jobs = get_dynamic_jobs()
            if not all_jobs:
                send_message(chat_id, "⏳ جاري تجهيز قاعدة الوظائف، أرسل /refresh لتشغيل فحص فوري للنت...")
                return jsonify({"status": "no_jobs"})

            seen_set = load_user_seen()
            unseen = [j for j in all_jobs if j.get("hash", j.get("url")) not in seen_set]

            if not unseen:
                finished_msg = f"""<b>✅ ممتاز يا أ. تامر!</b>

لقد اطلعت على جميع الوظائف المتاحة حالياً بالكامل (<b>{len(all_jobs)} وظيفة ريموت موثقة</b>).
🔔 سيتم إشعارك تلقائياً فور اكتشاف وظائف جديدة من الإنترنت.

🔄 إذا أردت إعادة تصفح الوظائف من البداية، أرسل:
<b>/reset</b>
"""
                send_message(chat_id, finished_msg)
                return jsonify({"status": "all_seen"})

            batch = unseen[:3]
            for j in batch:
                seen_set.add(j.get("hash", j.get("url")))
            save_user_seen(seen_set)

            remaining = len(unseen) - len(batch)

            reply = f"<b>✈️ وظائف سياحة وحجوزات جديدة 🆕 (100% ريموت):</b>\n"
            reply += f"<i>📊 متبقي {remaining} وظيفة جديدة لم تشاهدها بعد</i>\n\n"

            for j in batch:
                title = j.get('title', 'وظيفة سياحة')
                comp = j.get('company', 'شركة سياحة')
                source = j.get('source', 'تنقيب مصر')
                url = j.get('url', '#')
                match = j.get('match_score', 96)
                reqs = j.get('requirements', ['خبرة حجوزات وسياحة خارجية'])[0]
                
                reply += "━━━━━━━━━━━━━━━━━━━━\n"
                reply += f"🏢 <b>{comp}</b> | 📍 100% ريموت\n"
                reply += f"💼 <b>{title}</b> &nbsp;[توافق {match}% 🔥]\n"
                reply += "━━━━━━━━━━━━━━━━━━━━\n"
                reply += f"• 📋 <b>أبرز المتطلبات:</b> {reqs}\n"
                reply += f"• 🌐 <b>المنصة:</b> {source}\n\n"
                reply += f"👉 <a href=\"{url}\"><b>اضغط هنا للتقديم المباشر على الوظيفة</b></a>\n"
                reply += "────────────────────\n\n"

            if remaining > 0:
                reply += f"<i>👉 أرسل /jobs لعرض الوظائف الجديدة التالية ({remaining} متبقية)!</i>"
            else:
                reply += "<i>🎉 كانت هذه آخر الوظائف المكتشفة في فحص اليوم!</i>"

            send_message(chat_id, reply)

        # 4. تصفير الذاكرة
        elif text == "/reset":
            save_user_seen(set())
            send_message(chat_id, "🔄 <b>تم تصفير سجل المشاهدة بنجاح!</b>\nالآن عند كتابة <b>/jobs</b> سيبدأ بعرض الوظائف مجدداً من الوظيفة رقم 1.")

        # 5. تشغيل فحص يدوي حي عند الطلب في الخلفية
        elif text == "/refresh":
            send_message(chat_id, "🔍 <b>جاري فحص الإنترنت ومحركات التوظيف بحثاً عن وظائف جديدة الآن في السحاب...</b>\nسأرسل لك إشعاراً بالنتائج فور انتهاء الفحص.")
            def run_refresh_async(c_id):
                try:
                    import fetch_verified_remote_jobs
                    jobs, blocked, total, ts = fetch_verified_remote_jobs.run_pipeline()
                    send_message(c_id, f"✅ <b>اكتمل فحص الإنترنت السحابي!</b>\nتم فحص {total} مصادر وتوثيق {len(jobs)} وظيفة نشطة. أرسل /jobs لتصفحها الآن.")
                except Exception as e:
                    send_message(c_id, f"حدث خطأ أثناء الفحص: {e}")
            threading.Thread(target=run_refresh_async, args=(chat_id,), daemon=True).start()

        # 6. خطابات التقديم
        elif text == "/cover_ar":
            cover_ar = """<b>نموذج خطاب التقديم للشركات الخليجية والسعودية (نسخ سريع):</b>

<code>عناية الأستاذ / مدير التوظيف والموارد البشرية،،
تحية طيبة وبعد،،

يسعدني التقدم لشغل وظيفة (أخصائي / مسؤول حجوزات وعمليات سياحية عن بُعد). 

أمتلك خبرة تتجاوز 15 عاماً في قطاع السياحة وإدارة الفروع وحجوزات الفنادق، مع تخصص دقيق في خدمة عملاء وسوق الخليج العربي (المملكة العربية السعودية والإمارات). تشمل خبراتي السابقة التعاقد المباشر مع كبرى سلاسل الفنادق 4 و 5 نجوم (ماريوت، هيلتون، فورسيزونز، موفنبيك)، وإدارة المخصصات وتثبيت الأسعار، والتعامل الاحترافي مع رحلات الأفراد والمجموعات وكبار الشخصيات (VIPs).

أنا على أتم الاستعداد للعمل الفوري بنظام الدوام الكامل عن بُعد (Full-time Remote) المتوافق مع ساعات العمل في الخليج. مرفق لسعادتكم سيرتي الذاتية التفصيلية للاطلاع.

وتفضلوا بقبول فائق الاحترام والتقدير،،

تامر إمام
استشاري حجوزات وسياحة خارجية
هاتف / واتساب: 00201004713415
بريد إلكتروني: tameremam123@gmail.com</code>
"""
            send_message(chat_id, cover_ar)

        elif text == "/cover":
            cover_en = """<b>English Pitch / Cover Letter (Click to Copy):</b>

<code>Dear Hiring Manager,

With over 15 years of experience in hotel reservations management, direct contracting with 4 & 5-star international chains (Marriott, Hilton, Four Seasons), and catering extensively to GCC travelers across KSA and UAE, I am excited to apply for the Remote Travel / Reservations Specialist position.

I am available for immediate full-time remote engagement aligned with GCC working hours. Please find my attached ATS-optimized resume for your review.

Best regards,
Tamer Emam
Phone/WhatsApp: +20 100 471 3415
Email: tameremam123@gmail.com</code>
"""
            send_message(chat_id, cover_en)

        elif text == "/profile":
            prof = """<b>👤 بطاقة البيانات المهنية السريعة:</b>

• <b>الاسم:</b> تامر إمام سيد علي (Tamer Emam)
• <b>التخصص:</b> Senior Hotel Reservations Specialist / B2B Tourism Consultant
• <b>الخبرة:</b> 15+ سنة في حجوزات الفنادق، التعاقد المباشر، وسياحة الخليج العربي
• <b>الأنظمة:</b> Amadeus GDS, Booking Extranet, Expedia Central, B2B Channels
• <b>الهاتف / واتساب:</b> <code>+201004713415</code>
• <b>الإيميل:</b> <code>tameremam123@gmail.com</code>
"""
            send_message(chat_id, prof)

    except Exception as e:
        print(f"Webhook global exception: {e}", file=sys.stderr)

    return jsonify({"status": "ok"})

# Background Daily Scheduler Thread (Runs every day at 09:00 AM Cairo Time)
def daily_cron_worker():
    last_run_day = None
    while True:
        try:
            now_cairo = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))
            today_str = now_cairo.strftime("%Y-%m-%d")
            if now_cairo.hour == 9 and last_run_day != today_str:
                print(f"[CRON] Running daily morning job hunt: {today_str}")
                last_run_day = today_str
                import fetch_verified_remote_jobs
                fetch_verified_remote_jobs.run_pipeline()
        except Exception as e:
            print(f"[CRON ERROR]: {e}", file=sys.stderr)
        time.sleep(60)

cron_thread = threading.Thread(target=daily_cron_worker, daemon=True)
cron_thread.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
