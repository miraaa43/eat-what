import pandas as pd

menu_data = [
    # 熟成紅茶
    {"分類": "熟成紅茶", "品項": "熟成紅茶", "中杯價": 30, "大杯價": 35},
    {"分類": "熟成紅茶", "品項": "麗春紅茶", "中杯價": 30, "大杯價": 35},
    {"分類": "熟成紅茶", "品項": "熟成檸果", "中杯價": 50, "大杯價": 60},
    {"分類": "熟成紅茶", "品項": "白玉熟成紅茶", "中杯價": 45, "大杯價": 55},
    
    # 春梅系列
    {"分類": "春梅", "品項": "熟成春梅", "中杯價": 45, "大杯價": 55},
    {"分類": "春梅", "品項": "白玉春梅", "中杯價": 50, "大杯價": 60},
    
    # 醇奶茶系列
    {"分類": "醇奶茶", "品項": "熟成紅茶拿鐵", "中杯價": 50, "大杯價": 60},
    {"分類": "醇奶茶", "品項": "麗春紅茶拿鐵", "中杯價": 50, "大杯價": 60},
    {"分類": "醇奶茶", "品項": "白玉紅茶拿鐵", "中杯價": 55, "大杯價": 65},
    
    # 冬瓜系列
    {"分類": "冬瓜", "品項": "冬瓜熟成紅茶", "中杯價": 35, "大杯價": 45},
    {"分類": "冬瓜", "品項": "冬瓜檸檬", "中杯價": 40, "大杯價": 50},
    {"分類": "冬瓜", "品項": "白玉冬瓜", "中杯價": 45, "大杯價": 55},
    
    # 桂花系列（季節限定）
    {"分類": "桂花", "品項": "桂花釀紅茶", "中杯價": 45, "大杯價": 55},
    {"分類": "桂花", "品項": "桂花釀奶茶", "中杯價": 55, "大杯價": 65},
    {"分類": "桂花", "品項": "白玉桂花釀", "中杯價": 55, "大杯價": 65},
    
    # 氣泡飲
    {"分類": "氣泡飲", "品項": "熟成氣泡紅", "中杯價": 45, "大杯價": 55},
    {"分類": "氣泡飲", "品項": "熟成氣泡檸檬", "中杯價": 50, "大杯價": 60},
]

df = pd.DataFrame(menu_data)
df.to_csv("kebuke_menu.csv", index=False, encoding="utf-8-sig")
print("✅ 已儲存：可不可_菜單.csv")
