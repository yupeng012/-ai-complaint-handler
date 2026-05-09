import os
import sys
import requests

def send_telegram_message(message_text):
    """发送消息到 Telegram"""
    # 从环境变量读取 Token 和 Chat ID (Streamlit Cloud 上在 Secrets 里配置)
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        # 兼容本地测试，如果没有环境变量，尝试从本地文件读取（仅调试用）
        if os.path.exists("telegram_config.json"):
            import json
            with open("telegram_config.json") as f:
                config = json.load(f)
                token = config.get("token")
                chat_id = config.get("chat_id")
        else:
            return False, "Missing Telegram credentials"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            return True, "Sent successfully"
        else:
            return False, f"Telegram API Error: {response.text}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

if __name__ == "__main__":
    # 测试用
    if len(sys.argv) > 1:
        success, msg = send_telegram_message(sys.argv[1])
        print(f"{success}: {msg}")
    else:
        print("Usage: python telegram_notifier.py 'Your message here'")
