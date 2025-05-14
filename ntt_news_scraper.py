import requests
from bs4 import BeautifulSoup
import os

def get_ntt_news():
    url = 'https://news.yahoo.co.jp/rss/media/ntt/all.xml'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'xml')
    items = soup.find_all('item')[:3]  # 最新3件だけ

    messages = []
    for item in items:
        title = item.title.text
        link = item.link.text
        messages.append(f'{title}\n{link}')

    return '\n\n'.join(messages)

def send_line_notify(message):
    token = os.environ.get('LINE_NOTIFY_TOKEN')
    if not token:
        print("LINE_NOTIFY_TOKEN not set.")
        return

    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    payload = {'message': message}
    requests.post(url, headers=headers, data=payload)

if __name__ == '__main__':
    news = get_ntt_news()
    send_line_notify(f'【NTTニュース速報】\n\n{news}')
