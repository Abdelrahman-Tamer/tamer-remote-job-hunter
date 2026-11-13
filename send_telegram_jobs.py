import os
import sys
import requests

BOT_TOKEN = "9027811700:AAEma9XxUdpK9xb324h3nba8TJ2jLT6r9nQ"
CHAT_ID = "7660758855"

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
LATEST_MSG_FILE = os.path.join(WORKSPACE_DIR, "daily_job_reports", "latest_telegram_msg.txt")

def send_telegram_message(html_text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Telegram hard limit is 4096 chars per message.
    # Split text into clean chunks <= 3800 chars.
    if len(html_text) <= 3800:
        chunks = [html_text]
    else:
        parts = html_text.split("───────────────────")
        chunks = []
        current_chunk = ""
        for p in parts:
            p_formatted = p.strip()
            if not p_formatted:
                continue
            addition = p_formatted + "\n───────────────────\n"
            if len(current_chunk) + len(addition) > 3800:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = addition
            else:
                current_chunk += addition
        if current_chunk:
            chunks.append(current_chunk)

    all_success = True
    for idx, chunk in enumerate(chunks, 1):
        chunk_clean = chunk.strip()
        if not chunk_clean:
            continue
        payload = {
            "chat_id": CHAT_ID,
            "text": chunk_clean,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            print(f"Telegram chunk {idx}/{len(chunks)} sent successfully! Status: {r.status_code}")
        except Exception as e:
            print(f"Error sending chunk {idx} with HTML: {e}", file=sys.stderr)
            # Fallback to plain text if HTML tags cause a 400 parse error
            try:
                payload["parse_mode"] = None
                r2 = requests.post(url, json=payload, timeout=15)
                r2.raise_for_status()
                print(f"Telegram chunk {idx}/{len(chunks)} delivered via plain text fallback.")
            except Exception as e2:
                print(f"Error in fallback send: {e2}", file=sys.stderr)
                all_success = False

    return all_success

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "--sample":
        arg = sys.argv[1]
        if os.path.isfile(arg):
            with open(arg, "r", encoding="utf-8") as f:
                content = f.read()
            send_telegram_message(content)
        else:
            send_telegram_message(arg)
    else:
        if os.path.isfile(LATEST_MSG_FILE):
            with open(LATEST_MSG_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            send_telegram_message(content)
        else:
            print("No message file found. Run fetch_verified_remote_jobs.py first.")
