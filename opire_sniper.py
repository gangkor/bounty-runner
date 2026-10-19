import os
import requests
import json
import time

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8693469191:AAEaEszFTAibl8bUAnkqe9hDN3-p4DMB8A0")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "7572064021")
GITHUB_TOKEN = os.getenv("GH_TOKEN") or os.getenv("GH_PAT")

def send_telegram(message: str):
    """Надсилає сповіщення в @Giterbitter_bot"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print(f"[!] Telegram notify status: {r.status_code}, response: {r.text}")
    except Exception as e:
        print(f"[!] Telegram notify error: {e}")

def search_opire_bounties():
    """Шукає актуальні Issue із заблокованою нагородою від Opire"""
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    query = 'is:issue is:open "opire reward" in:comments sort:created-desc'
    url = f"https://api.github.com/search/issues?q={requests.utils.quote(query)}&per_page=15"
    print("[*] Сканування Opire.dev баунті...")
    res = requests.get(url, headers=headers, timeout=15)
    if res.status_code != 200:
        print(f"[!] Помилка пошуку GitHub: {res.status_code}")
        return []
    items = res.json().get("items", [])
    valid_tasks = []
    for item in items:
        issue_title = item.get("title")
        issue_url = item.get("html_url")
        repo_name = item.get("repository_url", "").replace("https://api.github.com/repos/", "")
        body = item.get("body", "") or ""
        if "pull_request" in item:
            continue
        valid_tasks.append({
            "repo": repo_name,
            "title": issue_title,
            "url": issue_url,
            "issue_number": item.get("number"),
            "body": body[:300]
        })
    return valid_tasks

def main():
    if not GITHUB_TOKEN:
        print("[!] GH_TOKEN відсутній!")
    send_telegram("🚀 *Opire Sniper ініціалізовано* на хмарному раннері.\nПочинаю перевірку активних баунті...")
    bounties = search_opire_bounties()
    if not bounties:
        print("[-] Наразі нових активних задач Opire не виявлено. Очікування наступного циклу.")
        return
    top_task = bounties[0]
    msg = (
        f"🎯 *ЗНАЙДЕНО OPIRE БАУНТІ!*\n\n"
        f"📁 *Репозиторій:* `{top_task['repo']}`\n"
        f"📌 *Задача:* {top_task['title']}\n"
        f"🔗 *Посилання:* [Відкрити Issue]({top_task['url']})\n\n"
        f"🤖 *Статус:* Завдання взято в аналіз ШІ для генерації фіксу."
    )
    send_telegram(msg)
    print(f"[+] Знайдено баунті: {top_task['repo']} #{top_task['issue_number']}")

if __name__ == "__main__":
    main()
