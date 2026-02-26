import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import os

# 从 GitHub Secrets 中读取敏感信息
API_KEY = os.environ.get('RAINFOREST_API_KEY')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD') 
ASIN = "B0FTKDC8C7"
SENDER_EMAIL = "1219068551@qq.com"
RECEIVER_EMAIL = "1219068551@qq.com"

def get_amazon_data():
    params = {
        'api_key': API_KEY,
        'type': 'product',
        'amazon_domain': 'amazon.com',
        'asin': ASIN
    }
    try:
        res = requests.get('https://api.rainforestapi.com/request', params=params, timeout=20)
        data = res.json()
        if not data.get("request_info", {}).get("success"): return None
        
        product = data.get("product", {})
        return {
            "rating": product.get("rating", 0),
            "ratings_total": product.get("ratings_total", 0),
            "bsr_rank": product.get("bestsellers_rank", [{}])[0].get("rank", "N/A"),
            "price": product.get("buybox_winner", {}).get("price", {}).get("value", 0)
        }
    except: return None

def send_email(new_data):
    subject = f"【监控报告】ASIN {ASIN} 状态更新"
    body = f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n" \
           f"⭐ 评分: {new_data['rating']}\n" \
           f"📈 评论总数: {new_data['ratings_total']}\n" \
           f"🏆 BSR排名: {new_data['bsr_rank']}\n" \
           f"💰 价格: ${new_data['price']}"

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = f"{Header('亚马逊助手', 'utf-8').encode()} <{SENDER_EMAIL}>"
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = Header(subject, "utf-8")

    with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

if __name__ == "__main__":
    data = get_amazon_data()
    if data:
        send_email(data)
        print("✅ 数据抓取并邮件发送成功")
