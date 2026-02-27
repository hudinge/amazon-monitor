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
        
        # 优化评论数提取逻辑
        # 尝试从不同的 API 字段中获取评论数
        reviews_count = product.get("reviews_total") 
        if reviews_count is None:
            # 备选方案：从汇总评分详情中计算
            reviews_count = product.get("sub_rating_counts", {}).get("total_reviews", 0)

        bsr_list = product.get("bestsellers_rank", [])
        main_rank = "N/A"
        sub_rank = "N/A"
        if bsr_list:
            main_rank = f"#{bsr_list[0].get('rank')} in {bsr_list[0].get('category')}"
            if len(bsr_list) > 1:
                sub_rank = f"#{bsr_list[1].get('rank')} in {bsr_list[1].get('category')}"

        return {
            "rating": product.get("rating", 0),
            "ratings_total": product.get("ratings_total", 0),
            "reviews_total": reviews_count, # 使用优化后的变量
            "bsr_main": main_rank,
            "bsr_sub": sub_rank
        }
    except Exception as e:
        print(f"Error: {e}")
        return None

def send_email(new_data):
    subject = f"【监控报告】ASIN {ASIN} 数据更新"
    body = f"核查时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n" \
           f"--------------------------\n" \
           f"⭐ 评分星级: {new_data['rating']}\n" \
           f"📊 Rating总数: {new_data['ratings_total']}\n" \
           f"💬 Review数量 (带文字): {new_data['reviews_total']}\n" \
           f"🏆 大类排名: {new_data['bsr_main']}\n" \
           f"🎖️ 小类排名: {new_data['bsr_sub']}\n" \
           f"--------------------------\n" \
           f"商品链接: https://www.amazon.com/dp/{ASIN}"

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = Header(subject, "utf-8")

    try:
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ 邮件发送成功")
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")

if __name__ == "__main__":
    data = get_amazon_data()
    if data:
        send_email(data)
    else:
        print("❌ 未能获取到有效数据")
