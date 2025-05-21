import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os

def get_ntt_news():
    url = 'https://news.yahoo.co.jp/rss/topics/top-picks.xml'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "ニュースの取得に失敗しました（ステータスコード: " + str(response.status_code) + "）"

    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')

    ntt_items = [item for item in items if 'NTT' in item.title.text]

    if not ntt_items:
        return "本日はNTT関連のニュースは見つかりませんでした。"

    messages = []
    for item in ntt_items[:3]:
        title = item.title.text
        link = item.link.text
        messages.append(f'{title}\n{link}')

    print("DEBUG NEWS:\n", '\n\n'.join(messages))
    return '\n\n'.join(messages)

def get_stock_prices():
    stock_codes = ['9343', '7378', '9264', '2107', '2498', '7164', '8424', '8425', '8584', '6411']
    headers = {'User-Agent': 'Mozilla/5.0'}
    stock_lines = []

    for code in stock_codes:
        url = f'https://finance.yahoo.co.jp/quote/{code}.T'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        try:
            name = soup.find('h1').text.strip()
            price = soup.find('span', attrs={'class': 'value'}).text.strip()
            stock_lines.append(f'{code} {name}：{price}円')
        except Exception as e:
            stock_lines.append(f'{code}：株価情報取得失敗')
            print(f'ERROR: {code} → {e}')

    return '\n'.join(stock_lines)

def send_email(message):
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_PASSWORD')
    to_email = os.environ.get('TO_EMAIL')

    # ←ここに追加！
    stock_summary = get_stock_prices()
    
    # メール本文（人間っぽくする）
    body = f"""こんにちは！

以下は本日のNTT関連ニュースです：

{message}

-------------------------------
【株価情報】
{stock_summary}
-------------------------------

良い一日を！
-- NTTニュースBot"""

    try:
        # メールのヘッダーと本文（エンコード明示）
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header('【NTTニュース+株価通知】本日のまとめ', 'utf-8')
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
    
