import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os

def get_ntt_news():
    url = 'https://news.yahoo.co.jp/rss/media/ntt/all.xml'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'xml')
    items = soup.find_all('item')[:3]
    
    messages = []
    for item in items:
        title = item.title.text
        link = item.link.text
        messages.append(f'{title}\n{link}')

    print("DEBUG NEWS:\n", '\n\n'.join(messages))  # ← これが正解！
    
    return '\n\n'.join(messages)

def send_email(message):
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_PASSWORD')
    to_email = os.environ.get('TO_EMAIL')

    print("DEBUG:", gmail_user, to_email)  # デバッグ確認用（削除してもOK）

    # メール本文（人間っぽくする）
    body = f"""こんにちは！

以下は本日のNTT関連ニュースです：

{message}

良い一日を！
-- NTTニュースBot"""

    try:
        # メールのヘッダーと本文（エンコード明示）
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header('【NTTニュース速報】本日のニュースまとめ', 'utf-8')
        msg['From'] = gmail_user
        msg['To'] = to_email

        # Gmail サーバへ送信
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()

        print('Email sent!')

    except Exception as e:
        print('Failed to send email:', str(e))

if __name__ == '__main__':
    news = get_ntt_news()
    send_email(news)
    
