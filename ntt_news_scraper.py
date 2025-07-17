import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os
import yfinance as yf

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

    return '\n\n'.join(messages)

def get_stock_prices():
    stock_codes = ['9343.T', '7378.T', '9264.T', '2498.T', '7164.T', '8424.T', '8425.T', '8584.T', '5491.T', '4578.T']
    stock_lines = []

    for code in stock_codes:
        try:
            stock = yf.Ticker(code)
            data = stock.history(period='1d')
            close_price = data['Close'].iloc[-1]
            stock_lines.append(f'{code}：終値 {round(close_price, 2)} 円')
        except Exception as e:
            stock_lines.append(f'{code}：取得失敗')
            print(f'ERROR: {code} → {e}')

    return '\n'.join(stock_lines)

def check_volume_ranking():
    url = 'https://kabutan.jp/warning/?mode=3_1'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    target_codes = ['9343', '7378', '9264', '2107', '2498', '7164', '8424', '8425', '8584', '6411']
    table = soup.find('table', class_='stock_table')
    if not table:
        return "出来高急増ランキングの取得に失敗しました。"

    rows = table.find_all('tr')[1:21]  # 上位20銘柄だけチェック
    matches = []

    for i, row in enumerate(rows, 1):
        cols = row.find_all('td')
        if not cols:
            continue
        code = cols[0].text.strip()
        name = cols[1].text.strip()
        if code in target_codes:
            matches.append(f"{i}位：{code} {name}")

    if matches:
        return "以下の銘柄が出来高急増ランキングにランクインしています：\n" + "\n".join(matches)
    else:
        return "本日は指定銘柄のランクインは確認できませんでした。"

def send_email(news_message):
    gmail_user = os.environ.get('GMAIL_USER')
    gmail_password = os.environ.get('GMAIL_PASSWORD')
    to_email = os.environ.get('TO_EMAIL')

    stock_summary = get_stock_prices()
    volume_alert = check_volume_ranking()
    
    body = f"""こんにちは！

以下は本日のNTT関連ニュースです：

{news_message}

-------------------------------
【株価情報】
{stock_summary}
-------------------------------
【出来高急増ランキング】
{volume_alert}
-------------------------------

良い一日を！
-- NTTニュースBot"""

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header('【NTTニュース+株価通知】本日のまとめ', 'utf-8')
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
    print("DEBUG NEWS:\n", news)
    send_email(news)
