import requests
from bs4 import BeautifulSoup
import schedule
import time
from twilio.rest import Client
import sys
sys.stdout.reconfigure(encoding='utf-8')

# بيانات Twilio
TWILIO_SID = "ACbd382a3388c435e9cb005dbcb618ec32"
TWILIO_AUTH_TOKEN = "20b2b08fd5d2ca21424982288c7a737a"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # رقم Twilio للواتساب
YOUR_WHATSAPP_NUMBER = "whatsapp:+966509770860"  # رقمك الشخصي

def send_whatsapp_message(message):
    """ إرسال إشعار عبر واتساب عند تغيير حالة المنتج """
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=message,
        to=YOUR_WHATSAPP_NUMBER
    )
    print("📩 تم إرسال إشعار واتساب!")

def check_amazon_stock(url):
    """ التحقق من حالة المنتج في أمازون """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ فشل في جلب الصفحة: {url}")
        return False
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # البحث عن حالة المخزون
    stock_text = soup.text
    
    if "غير متوفر" in stock_text:
        print(f"⚠️ المنتج غير متوفر: {url}")
        send_whatsapp_message(f"🔴 المنتج غير متوفر: {url}")
        return False
    
    if "لا يوجد عروض متوفرة" in stock_text:
        print(f"⚠️ لا يوجد عروض متوفرة لهذا المنتج: {url}")
        send_whatsapp_message(f"🟠 لا يوجد عروض متوفرة لهذا المنتج: {url}")
        return False

    print(f"✅ المنتج متاح في المخزون: {url}")
    return True

def daily_stock_check():
    """ التحقق من جميع المنتجات يوميًا """
    product_urls = [
        "https://www.amazon.sa/dp/B0CTJF2L8H",
        "https://amzn.eu/d/0N3nSz0",  
        "https://amzn.eu/d/0wehpMr"
    ]
    for url in product_urls:
        check_amazon_stock(url)
    print("✅ تم التحقق من المنتجات اليوم!")

# جدولة الفحص ليتم يوميًا في الساعة 8 صباحًا
schedule.every().day.at("08:00").do(daily_stock_check)

print("🔄 البوت يعمل الآن وسيتحقق من المخزون يوميًا في الساعة 8 صباحًا...")
while True:
    schedule.run_pending()
    time.sleep(60)  # فحص الجدولة كل دقيقة
