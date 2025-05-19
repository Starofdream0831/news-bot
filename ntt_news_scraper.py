import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
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

    return '\n\n'.join(messages)

def send_email(message):
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_PASSWORD')
    to_email = os.environ.get('TO_EMAIL')

    print("DEBUG:", gmail_user, to_email)  # ← 追加！
    
    msg = MIMEText(message)
    msg['Subject'] = '【NTTニュース速報】'
    msg['From'] = gmail_user
    msg['To'] = to_email

    try:
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
