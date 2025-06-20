import pandas as pd

menu_data = [
    # 棉被系列（奶蓋）
    {"分類": "棉被系列", "品項": "棉被日安紅", "中杯": 60, "大杯": 75},
    {"分類": "棉被系列", "品項": "棉被午茉綠", "中杯": 60, "大杯": 75},
    {"分類": "棉被系列", "品項": "棉被四季金萱", "中杯": 60, "大杯": 75},
    {"分類": "棉被系列", "品項": "棉被深焙烏龍", "中杯": 60, "大杯": 75},
    {"分類": "棉被系列", "品項": "棉被熟八蕎麥", "中杯": 60, "大杯": 75},

    # 歐蕾系列（鮮奶茶）
    {"分類": "歐蕾系列", "品項": "日安紅歐蕾", "中杯": 65, "大杯": 75},
    {"分類": "歐蕾系列", "品項": "午茉綠歐蕾", "中杯": 65, "大杯": 75},
    {"分類": "歐蕾系列", "品項": "四季金萱歐蕾", "中杯": 65, "大杯": 75},
    {"分類": "歐蕾系列", "品項": "深焙烏龍歐蕾", "中杯": 65, "大杯": 75},
    {"分類": "歐蕾系列", "品項": "熟八蕎麥歐蕾", "中杯": 65, "大杯": 75},
    {"分類": "歐蕾系列", "品項": "熟八蕎麥燕麥歐蕾", "中杯": 70, "大杯": 80},

    # 純茶系列
    {"分類": "純茶系列", "品項": "日安紅", "中杯": 35, "大杯": 40},
    {"分類": "純茶系列", "品項": "午茉綠", "中杯": 35, "大杯": 40},
    {"分類": "純茶系列", "品項": "四季春", "中杯": 35, "大杯": 40},
    {"分類": "純茶系列", "品項": "深焙烏龍", "中杯": 35, "大杯": 40},
    {"分類": "純茶系列", "品項": "熟八蕎麥", "中杯": 35, "大杯": 40},
    {"分類": "純茶系列", "品項": "桂香金萱", "中杯": 40, "大杯": 40},

    # 果茶系列
    {"分類": "果茶系列", "品項": "柚紅柚綠", "中杯": 65, "大杯": None},
    {"分類": "果茶系列", "品項": "芭檸年代", "中杯": 65, "大杯": None},
    {"分類": "果茶系列", "品項": "檸檬午茉", "中杯": 50, "大杯": 60},

    # 好濃鮮奶系列
    {"分類": "好濃鮮奶系列", "品項": "黑糖珍珠好濃鮮奶", "中杯": 75, "大杯": None},
    {"分類": "好濃鮮奶系列", "品項": "嫩仙草好濃鮮奶", "中杯": 75, "大杯": None},

    # 芋頭系列
    {"分類": "芋頭系列", "品項": "香芋啵啵", "中杯": 85, "大杯": None},
    {"分類": "芋頭系列", "品項": "黑糖香芋啵啵", "中杯": 85, "大杯": None},
]

df = pd.DataFrame(menu_data)
df.to_csv("naptea_menu.csv", index=False, encoding="utf-8-sig")

print("✅ 再睡五分鐘菜單已儲存為 naptea_menu.csv")