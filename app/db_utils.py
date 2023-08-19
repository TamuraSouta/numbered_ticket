import sqlite3
import hashlib

# データベースの初期設定
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            gender TEXT,
            age INTEGER,
            email TEXT
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            num_people INTEGER,
            store_id INTEGER
        )""")
        conn.execute("""
        CREATE TABLE IF NOT EXISTS stores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_id TEXT,
            store_name TEXT,
            password TEXT,
            phone_number TEXT,
            email TEXT,
            address TEXT
        )""")
        conn.commit()
        try:
            conn.commit()
        except sqlite3.OperationalError as e:
            # カラムが既に存在する場合はこのエラーを無視
            pass

# ユーザーの追加
def add_user(username, password, gender, age, email):  
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        with sqlite3.connect('users.db') as conn:
            conn.execute("INSERT INTO users (username, password, gender, age, email) VALUES (?, ?, ?, ?, ?)", (username, hashed_password, gender, age, email))
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# ユーザー認証
def authenticate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        stored_password = cur.fetchone()
        if stored_password and stored_password[0] == hashed_password:
            return True
        else:
            return False
        
#整理券発行関数
def issue_ticket(username, num_people, store_id):
    with sqlite3.connect('users.db') as conn:
        conn.execute("INSERT INTO tickets (username, num_people, store_id) VALUES (?, ?, ?)", (username, num_people, store_id))
        conn.commit()
        cur = conn.cursor()
        cur.execute("SELECT id FROM tickets WHERE username = ? ORDER BY id DESC LIMIT 1", (username,))
        ticket_id = cur.fetchone()
        return ticket_id[0], num_people 
    
# 整理券情報の取得
def get_previous_ticket(username, store_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, num_people, store_id FROM tickets WHERE username = ? AND store_id = ? ORDER BY id DESC LIMIT 1", 
                    (username, store_id))
        ticket_info = cur.fetchone()
        return ticket_info

# 整理券のキャンセル
def cancel_ticket(username, store_id):
    with sqlite3.connect('users.db') as conn:
        conn.execute("DELETE FROM tickets WHERE username = ? AND store_id = ?", (username, store_id))
        conn.commit()

#　店情報を取得
def get_store_info(store_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        
        cur.execute("SELECT store_name, phone_number, address FROM stores WHERE id = ?", (store_id,))
        store_info = cur.fetchone()
        return store_info

#　店ログイン照会
def authenticate_store(store_id, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT password FROM stores WHERE store_id = ?", (store_id,))
        stored_password = cur.fetchone()
        if stored_password and stored_password[0] == hashed_password:
            return True
        else:
            return False
        
# 店登録
def register_store(store_id, store_name, password, phone_number, email, address):  
    with sqlite3.connect('users.db') as conn:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn.execute("INSERT INTO stores (store_id, store_name, password, phone_number, email, address) VALUES (?, ?, ?, ?, ?, ?)", (store_id, store_name, hashed_password, phone_number, email, address))
        conn.commit()
    
# 店が存在するか確認
def check_store_exists(store_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM stores WHERE store_id = ?", (store_id,))
        result = cur.fetchone()
        return True if result else False
    
# IDがデータベースに存在するか確認
def check_store_id_exists(store_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT store_id FROM stores WHERE store_id = ?", (store_id,))
        result = cur.fetchone()
        return True if result else False



