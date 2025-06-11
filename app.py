from flask import Flask, request, abort
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient, TextMessage, ReplyMessageRequest
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging.models import (
    QuickReply, QuickReplyItem, MessageAction, ButtonsTemplate, TemplateMessage
)
import os
import csv
import random
import urllib.parse

app = Flask(__name__)

# LINE Bot 設定
CHANNEL_ACCESS_TOKEN = "rw3FhodzOY8eB+G0CRyhKjW31Oezn4lIbkUBV8pUtsVoHcjD5dpj1tRdKnL9CIOUX702fQTNPQSHRI8dsIFPaIudFfsT45asUsSPdnU6gxG15uWYmXw4hZ5Tb9kNm2eYw7t/oLxNMhcGKvcYEgy/IgdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "20a62af28d8e365c60276f948773385e"

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

api_client = ApiClient(configuration)
line_bot_api = MessagingApi(api_client)

# 餐廳資料載入
restaurants = []
with open("cleaned_meal_district.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cleaned = {k.strip(): (v.strip() if v else "") for k, v in row.items()}
        try:
            cleaned["meal_type"] = int(cleaned.get("meal_type", 0))
        except:
            cleaned["meal_type"] = 0
        restaurants.append(cleaned)

# 飲料資料載入
drinkItems = []
drink_dir = "drink_data"
for filename in os.listdir(drink_dir):
    if filename.endswith(".csv"):
        brand_name = filename.replace("_menu.csv", "").replace(".csv", "")
        with open(os.path.join(drink_dir, filename), encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned = {k.strip(): (v.strip() if v else "") for k, v in row.items()}
                cleaned["brand"] = brand_name
                cleaned["name"] = cleaned.get("品項", "")
                cleaned["mediumPrice"] = cleaned.get("中杯價") or cleaned.get("中杯") or ""
                cleaned["largePrice"] = cleaned.get("大杯價") or cleaned.get("大杯") or ""
                cleaned["price"] = cleaned.get("價格", "")
                cleaned["category"] = cleaned.get("分類", "無")
                drinkItems.append(cleaned)

brandMap = {
    "chaffee": "茶湯會", "chage": "茶聚", "chingshin": "清心福全", "coco": "CoCo都可",
    "comebuy": "ComeBuy", "dayung": "大苑子", "guiji": "龜記", "hachiyo": "八曜和茶",
    "jenjudan": "珍煮丹", "kebuke": "可不可", "maku": "麻古茶坊", "milksha": "迷客夏",
    "naptea": "再睡五分鐘", "wanpo": "萬波", "wutong": "五桐號", "yimir": "一沐日",
    "tptea": "茶湯會", "50lan": "五十嵐"
}
userDrinkState = {}

mealTypes = ["台式", "義式", "日式", "韓式", "美式", "中式", "粵式", "其他"]
districts = [
    "中山區", "松山區", "大安區", "信義區", "中正區",
    "萬華區", "北投區", "士林區", "大同區", "南港區", "內湖區", "文山區"
]

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    msg = event.message.text.strip()
    user_id = event.source.user_id
    reply_token = event.reply_token

    if msg == "使用說明":
        text = (
            "🔹 正餐\n點選選單的「正餐」，系統會依照地區推薦附近的餐廳。\n\n"
            "🔹 點心\n想吃甜點或下午茶？點選「點心」即可獲得推薦。\n\n"
            "🔹 飲料\n點選「飲料」→ 系統會推薦3家有賣的飲料店\n"
            "如果不喜歡，請輸入「換一批」來看下一輪選擇\n"
            "選擇店家後，還會推薦3個熱門品項給你！\n\n"
            "🔹 行政區查詢\n你可以依照行政區篩選店家\n\n"
            "📝 這是一個專屬台北市的推薦機器人，祝你每天都吃得開心！"
        )
        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=reply_token, messages=[TextMessage(text=text)]
        ))
        return

    if msg == "正餐":
        quick = QuickReply(items=[
            QuickReplyItem(action=MessageAction(label=t, text=t)) for t in mealTypes
        ])
        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=reply_token, messages=[TextMessage(text="請選擇餐點類型：", quick_reply=quick)]
        ))
        return

    if msg in mealTypes:
        filtered = [r for r in restaurants if r.get("meal_type") == 0 and r.get("sub_category") == msg]
        r = random.choice(filtered) if filtered else None
        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=f"為你推薦 {msg} 餐廳："), formatRestaurant(r)]
        ))
        return

    if msg == "行政區":
        quick = QuickReply(items=[
            QuickReplyItem(action=MessageAction(label=d, text=d)) for d in districts
        ])
        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=reply_token, messages=[TextMessage(text="請選擇行政區：", quick_reply=quick)]
        ))
        return

    if msg in districts:
        filtered = [r for r in restaurants if r.get("district") == msg and r.get("meal_type") == 0]
        r = random.choice(filtered) if filtered else None
        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=f"在 {msg} 找到的餐廳推薦："), formatRestaurant(r)]
        ))
        return

    if msg == "點心":
        filtered = [r for r in restaurants if r.get("meal_type") == 1]
        r = random.choice(filtered) if filtered else None
        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=reply_token, messages=[formatRestaurant(r)]
        ))
        return

    # 這裡可接續補上飲料推薦流程
    line_bot_api.reply_message(ReplyMessageRequest(
        reply_token=reply_token,
        messages=[TextMessage(text="請輸入：正餐、點心、行政區、飲料、使用說明")]
    ))

def formatRestaurant(r):
    if not r:
        return TextMessage(text="找不到符合的餐廳喔～")
    name = r.get("restaurant_title", "無店名")
    address = r.get("restaurant_address", "無地址")
    query = urllib.parse.quote_plus(f"{name} {address}")
    link = f"https://www.google.com/maps/search/?api=1&query={query}"
    return TextMessage(text=f"餐廳名稱：{name}\n地址：{address}\n{link}")

if __name__ == "__main__":
    app.run(port=3000, debug=True)
