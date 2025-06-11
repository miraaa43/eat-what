const express = require("express");
const line = require("@line/bot-sdk");
const fs = require("fs");
const csv = require("csv-parser");
const path = require("path");

const app = express();
const port = process.env.PORT || 3000;

const config = {
  channelAccessToken: "rw3FhodzOY8eB+G0CRyhKjW31Oezn4lIbkUBV8pUtsVoHcjD5dpj1tRdKnL9CIOUX702fQTNPQSHRI8dsIFPaIudFfsT45asUsSPdnU6gxG15uWYmXw4hZ5Tb9kNm2eYw7t/oLxNMhcGKvcYEgy/IgdB04t89/1O/w1cDnyilFU=",
  channelSecret: "20a62af28d8e365c60276f948773385e"
};
const client = new line.Client(config);

// 讀取餐廳資料
let restaurants = [];
fs.createReadStream("cleaned_meal_district.csv")
  .pipe(csv())
  .on("data", (row) => {
    const cleanedRow = {};
    Object.keys(row).forEach((key) => {
      const cleanKey = key.trim();
      cleanedRow[cleanKey] = row[key] ? row[key].trim() : "";
    });
    restaurants.push(cleanedRow);
  })
  .on("end", () => console.log("✅ 餐廳資料載入完成，共:", restaurants.length));

// 讀取飲料資料
const drinkDir = path.join(__dirname, "drink_data");
let drinkItems = [];

const drinkFiles = fs.readdirSync(drinkDir).filter(file => file.endsWith(".csv"));
Promise.all(drinkFiles.map(file => {
  return new Promise((resolve, reject) => {
    const brandName = file.replace("_menu.csv", "").replace(".csv", "");
    fs.createReadStream(path.join(drinkDir, file))
      .pipe(csv())
      .on("headers", (headers) => {
        headers.forEach((h, i) => headers[i] = h.trim());
      })
      .on("data", row => {
        const cleanedRow = {};
        Object.keys(row).forEach(key => {
          const cleanKey = key.trim();
          cleanedRow[cleanKey] = row[key] ? row[key].trim() : "";
        });

        cleanedRow.brand = brandName;
        cleanedRow.name = cleanedRow["品項"] || "";
        cleanedRow.mediumPrice = cleanedRow["中杯價"] || cleanedRow["中杯"] || "";
        cleanedRow.largePrice = cleanedRow["大杯價"] || cleanedRow["大杯"] || "";
        cleanedRow.price = cleanedRow["價格"] || "";
        cleanedRow.category = cleanedRow["分類"] || "無";

        drinkItems.push(cleanedRow);
      })
      .on("end", resolve)
      .on("error", reject);
  });
})).then(() => {
  console.log("✅ 所有飲料店載入完成，共:", drinkItems.length, "筆");
});

const brandMap = {
  chaffee: "茶湯會", chage: "茶聚", chingshin: "清心福全", coco: "CoCo都可",
  comebuy: "ComeBuy", dayung: "大苑子", guiji: "龜記", hachiyo: "八曜和茶",
  jenjudan: "珍煮丹", kebuke: "可不可", maku: "麻古茶坊", milksha: "迷客夏",
  naptea: "再睡五分鐘", wanpo: "萬波", wutong: "五桐號", yimir: "一沐日",
  tptea: "茶湯會", "50lan": "五十嵐"
};

const userDrinkState = {};

const mealTypes = ["台式", "義式", "日式", "韓式", "美式", "中式", "粵式", "其他"];
const districts = [
  "中山區", "松山區", "大安區", "信義區", "中正區",
  "萬華區", "北投區", "士林區", "大同區", "南港區",
  "內湖區", "文山區"
];

app.post("/webhook", line.middleware(config), (req, res) => {
  Promise.all(req.body.events.map(handleEvent))
    .then((result) => res.json(result))
    .catch((err) => {
      console.error(err);
      res.status(500).end();
    });
});

async function handleEvent(event) {
  if (event.type !== "message" || event.message.type !== "text") return null;
  const msg = event.message.text.trim();
  const userId = event.source.userId;

  if (msg === "使用說明") {
    const instructions = `🔹 正餐
點選選單的「正餐」，系統會依照地區推薦附近的餐廳。

🔹 點心
想吃甜點或下午茶？點選「點心」即可獲得推薦。

🔹 飲料
點選「飲料」→ 系統會推薦3家有賣的飲料店
如果不喜歡，請輸入「換一批」來看下一輪選擇
選擇店家後，還會推薦3個熱門品項給你！

🔹 行政區查詢
你可以依照行政區篩選店家

🔹 快速開始
不知道要打什麼？直接點選選單就可以開始體驗！

📝 小提醒：
這是一個專屬台北市的推薦機器人～
有任何建議歡迎回報給我們 🙌
祝你每天都吃得開心！`;

    return client.replyMessage(event.replyToken, {
      type: "text",
      text: instructions
    });
  }

  if (msg === "正餐") {
    return client.replyMessage(event.replyToken, {
      type: "text",
      text: "請選擇餐點類型：",
      quickReply: {
        items: mealTypes.map(type => ({
          type: "action",
          action: { type: "message", label: type, text: type }
        }))
      }
    });
  }

  if (mealTypes.includes(msg)) {
    const filtered = restaurants.filter(r => r.meal_type === "0" && r.sub_category === msg);
    const result = randomPick(filtered);
    return client.replyMessage(event.replyToken, [
      { type: "text", text: `為你推薦 ${msg} 餐廳：` },
      formatRestaurant(result)
    ]);
  }

  if (msg === "行政區") {
    return client.replyMessage(event.replyToken, {
      type: "text",
      text: "請選擇行政區：",
      quickReply: {
        items: districts.map(d => ({
          type: "action",
          action: { type: "message", label: d, text: d }
        }))
      }
    });
  }

  if (districts.includes(msg)) {
    const filtered = restaurants.filter(r => r.district === msg && r.meal_type === "0");
    const result = randomPick(filtered);
    return client.replyMessage(event.replyToken, [
      { type: "text", text: `在 ${msg} 找到的餐廳推薦：` },
      formatRestaurant(result)
    ]);
  }

  if (msg === "點心") {
    const filtered = restaurants.filter(r => r.meal_type === "1");
    const result = randomPick(filtered);
    return client.replyMessage(event.replyToken, formatRestaurant(result));
  }

  if (msg === "飲料") {
    const candidates = [...new Set(drinkItems.map(d => d.brand))];
    const picks = randomSample(candidates, 3);
    userDrinkState[userId] = { step: "brand", seenBrands: [...picks] };
    return client.replyMessage(event.replyToken, formatBrandCarousel(picks));
  }

  if (msg === "都不喜歡" && userDrinkState[userId]?.step === "brand") {
    const seen = new Set(userDrinkState[userId].seenBrands);
    const remaining = [...new Set(drinkItems.map(d => d.brand))].filter(b => !seen.has(b));

    if (remaining.length === 0) {
      return client.replyMessage(event.replyToken, { type: "text", text: "已經沒有其他飲料店囉～" });
    }

    const picks = randomSample(remaining, 3);
    userDrinkState[userId].seenBrands = [...seen, ...picks];
    return client.replyMessage(event.replyToken, formatBrandCarousel(picks));
  }

  if (userDrinkState[userId]?.step === "brand") {
    const brandKey = Object.keys(brandMap).find(k => brandMap[k] === msg);
    if (!brandKey) {
      return client.replyMessage(event.replyToken, { type: "text", text: "找不到對應的品牌喔～" });
    }

    const brandItems = drinkItems.filter(d => d.brand === brandKey);
    const picks = randomSample(brandItems, 3);
    userDrinkState[userId] = { step: "item", brand: brandKey, seenItems: picks.map(p => p.name) };
    return client.replyMessage(event.replyToken, formatItemCarousel(picks));
  }

  if (msg === "想喝別的" && userDrinkState[userId]?.step === "item") {
    const { brand, seenItems } = userDrinkState[userId];
    const candidates = drinkItems.filter(d => d.brand === brand && !seenItems.includes(d.name));

    if (candidates.length === 0) {
      return client.replyMessage(event.replyToken, { type: "text", text: "已經沒有其他品項囉～" });
    }

    const picks = randomSample(candidates, 3);
    userDrinkState[userId].seenItems = [...new Set([...seenItems, ...picks.map(p => p.name)])];
    return client.replyMessage(event.replyToken, formatItemCarousel(picks));
  }

  if (userDrinkState[userId]?.step === "item") {
    const item = drinkItems.find(d => d.name === msg);
    if (item) {
      const category = item.category || "無";
      const name = item.name || "無品項名稱";
      const medium = item.mediumPrice;
      const large = item.largePrice;
      const price = item.price;

      let priceInfo = "";
      if (medium || large) {
        priceInfo += medium ? `中杯：${medium} 元\n` : "";
        priceInfo += large ? `大杯：${large} 元` : "";
      } else if (price) {
        priceInfo = `價格：${price} 元`;
      } else {
        priceInfo = "價格資訊無法提供";
      }

      return client.replyMessage(event.replyToken, {
        type: "text",
        text: `分類：${category}\n品項：${name}\n${priceInfo}`
      });
    }
  }

  return client.replyMessage(event.replyToken, {
    type: "text",
    text: "請輸入：正餐、點心、行政區、飲料、使用說明"
  });
}

// ✅ Google Maps 連結格式的餐廳顯示方式
function formatRestaurant(r) {
  if (!r) return { type: "text", text: "找不到符合的餐廳喔～" };

  const name = r.restaurant_title || "無店名";
  const address = r.restaurant_address || "無地址";
  const query = encodeURIComponent(`${name} ${address}`);
  const googleMapUrl = `https://www.google.com/maps/search/?api=1&query=${query}`;

  return {
    type: "text",
    text: `餐廳名稱：${name}\n地址：${address}\n${googleMapUrl}`
  };
}

function randomPick(arr) {
  if (arr.length === 0) return null;
  return arr[Math.floor(Math.random() * arr.length)];
}

function randomSample(arr, n) {
  const shuffled = [...arr].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

function formatBrandCarousel(brands) {
  return {
    type: "template",
    altText: "推薦飲料店",
    template: {
      type: "buttons",
      title: "推薦飲料店",
      text: "請選擇一家店或點 \"都不喜歡\"",
      actions: brands.map(b => ({
        type: "message",
        label: brandMap[b] || b,
        text: brandMap[b] || b
      })).concat({ type: "message", label: "都不喜歡", text: "都不喜歡" })
    }
  };
}

function formatItemCarousel(items) {
  return {
    type: "template",
    altText: "推薦飲料品項",
    template: {
      type: "buttons",
      title: "推薦飲料品項",
      text: "想喝哪一杯？",
      actions: items.slice(0, 3).map(i => ({
        type: "message",
        label: i.name.slice(0, 20),
        text: i.name
      })).concat({ type: "message", label: "想喝別的", text: "想喝別的" })
    }
  };
}

app.listen(port, () => {
  console.log(`🚀 伺服器啟動於 http://localhost:${port}`);
});
