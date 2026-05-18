import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker('zh_CN')

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # 订单表：集成类别和客户地区更方便
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date TEXT,
            product_category TEXT,
            region TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL
        )
    ''')
    conn.commit()
    return conn

def generate_data(db_path, num_records=2000):
    conn = init_db(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders")
    if cur.fetchone()[0] > 0:
        print("数据已存在，跳过生成")
        conn.close()
        return
    categories = ['电子产品', '服装', '家居', '食品', '运动户外']
    regions = ['华东', '华南', '华北', '西南', '西北']
    start_date = datetime(2024, 1, 1)
    print(f"正在生成 {num_records} 条模拟订单...")
    for _ in range(num_records):
        order_date = start_date + timedelta(days=random.randint(0, 364))
        cat = random.choice(categories)
        region = random.choice(regions)
        qty = random.randint(1, 5)
        if cat == '电子产品':
            price = round(random.uniform(500, 5000), 2)
        elif cat == '服装':
            price = round(random.uniform(50, 500), 2)
        elif cat == '家居':
            price = round(random.uniform(100, 2000), 2)
        elif cat == '食品':
            price = round(random.uniform(10, 200), 2)
        else:
            price = round(random.uniform(30, 800), 2)
        total = round(qty * price, 2)
        cur.execute(
            "INSERT INTO orders (order_date, product_category, region, quantity, unit_price, total_amount) VALUES (?,?,?,?,?,?)",
            (order_date.strftime("%Y-%m-%d"), cat, region, qty, price, total)
        )
    conn.commit()
    conn.close()
    print("数据生成完成")