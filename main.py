import streamlit as st
import pandas as pd

import sqlite3
import hashlib

# データベースの初期設定
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
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
            name TEXT,  
            phone_number TEXT,
            address TEXT
        )""")
        conn.commit()
        try:
            conn.execute("ALTER TABLE stores ADD COLUMN name TEXT")
            conn.commit()
        except sqlite3.OperationalError as e:
            # カラムが既に存在する場合はこのエラーを無視
            pass

# ユーザーの追加
def add_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    try:
        with sqlite3.connect('users.db') as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
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

#セッション状態の初期設定
if 'page' not in st.session_state:
    st.session_state.page = 'login'
    st.session_state.store_id = 1  # デフォルトの店のIDを設定


def main():
    # クエリパラメータから店のIDを取得
    params = st.experimental_get_query_params()
    store_id_from_url = params.get("store_id")
    if store_id_from_url:
        st.session_state.store_id = int(store_id_from_url[0])
    
    init_db()

    if st.session_state.page == 'login':
        display_login_page()
    elif st.session_state.page == 'register':
        display_register_page()
    elif st.session_state.page == 'issue_ticket':
        display_ticket_issue_page()
    elif st.session_state.page == 'show_ticket':
        display_ticket_show_page()
    elif st.session_state.page == 'main':
        display_main_page() 
    elif st.session_state.page == 'store_register': 
        display_store_register_page()

#ログイン画面
def display_login_page():
    st.subheader("ログイン画面")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type='password')
        
    if st.button("ログイン"):
        if authenticate_user(username, password):
            st.session_state.username = username 
            st.session_state.page = 'main' 
            st.experimental_rerun()  
        else:
            st.warning("ユーザー名またはパスワードが間違っています。")

    # 新規登録画面に遷移
    if st.button("新規登録画面へ"):
        st.session_state.page = 'register'
        st.experimental_rerun()
    # お店登録画面に遷移
    if st.button("お店の登録"):  
        st.session_state.page = 'store_register' 
        st.experimental_rerun()

#新規登録画面
def display_register_page():
    st.subheader("新規登録")
    
    new_username = st.text_input("新しいユーザー名")
    new_password = st.text_input("新しいパスワード", type='password')
    
    if st.button("登録"):
        if add_user(new_username, new_password):
            st.success("ユーザーが正常に登録されました。")
            st.session_state.page = 'login'  
            st.experimental_rerun()  

        else:
            st.warning("そのユーザー名は既に存在します。")

    # ログイン画面に戻るボタン
    if st.button("戻る"):
        st.session_state.page = 'login'
        st.experimental_rerun()  

# お店登録画面
def display_store_register_page():
    st.subheader("お店の登録")
    
    name = st.text_input("お店の名前")
    phone_number = st.text_input("電話番号")
    address = st.text_input("住所")
    
    if st.button("お店を登録"):
        store_id = register_store(name, phone_number, address)  # nameを引数として追加
        st.success(f"お店が正常に登録されました。お店のIDは{store_id}です。")
        if st.button("戻る"):
            st.session_state.page = 'login'
            st.experimental_rerun() 
        
#メイン画面
def display_main_page():
    st.subheader("メイン画面")
    
    store_info = get_store_info(st.session_state.store_id)
    if store_info:
        st.write(f"お店の名前: {store_info[0]}")  # お店の名前を表示

    if st.button("発行番号の確認"):
        st.session_state.page = 'show_ticket'
        st.experimental_rerun()
    if st.button("新規発行"):
        st.session_state.page = 'issue_ticket'
        st.experimental_rerun()

#発行券発行画面
def display_ticket_issue_page():
    st.subheader("整理券発行")
    
    num_people = st.number_input("人数を入力してください", min_value=1, max_value=100, value=1)
    if st.button("整理券を発行"):
        # store_idを追加して関数を呼び出します
        ticket_num, issued_num_people = issue_ticket(st.session_state.username, num_people, st.session_state.store_id)
        st.session_state.ticket_num = ticket_num
        st.session_state.issued_num_people = issued_num_people
        st.session_state.page = 'show_ticket'
        st.experimental_rerun()
    if st.button("戻る"):
        st.session_state.page = 'main'
        st.experimental_rerun() 

#発行券確認画面 
def display_ticket_show_page():
    st.subheader("発行された整理券の情報")
    ticket_info = get_previous_ticket(st.session_state.username)
    
    if ticket_info:
        st.write(f"整理券番号: {ticket_info[0]}")
        st.write(f"人数: {ticket_info[1]}")
        
        # お店の情報を取得
        store_info = get_store_info(ticket_info[2])
        if store_info:
            st.write(f"電話番号: {store_info[1]}")
            st.write(f"住所: {store_info[2]}")
            data = pd.DataFrame({
                'latitude': [35.685175],
                'longitude': [139.752800]
                })
            # highlight = pd.DataFrame({
            #     'latitude': [37.7749],
            #     'longitude': [-122.4194]
            #     })
            
            st.map(data)
            
            # # 住所のマップを表示
            # st.map({"lat": store_info[2], "lon": store_info[3]})
    else:
        st.write("まだ整理券は発行されていまaせん。")
        if st.button("新規発行"):
            st.session_state.page = 'issue_ticket'
            st.experimental_rerun()


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
def get_previous_ticket(username):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, num_people, store_id FROM tickets WHERE username = ? ORDER BY id DESC LIMIT 1", (username,))
        ticket_info = cur.fetchone()
        return ticket_info

#　店情報を取得
def get_store_info(store_id):
    with sqlite3.connect('users.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, phone_number, address FROM stores WHERE id = ?", (store_id,))
        store_info = cur.fetchone()
        return store_info
# 店登録
def register_store(name, phone_number, address):  # 引数としてnameを追加
    with sqlite3.connect('users.db') as conn:
        conn.execute("INSERT INTO stores (name, phone_number, address) VALUES (?, ?, ?)", (name, phone_number, address))
        conn.commit()
        
        # 追加したお店のIDを取得
        cur = conn.cursor()
        cur.execute("SELECT id FROM stores WHERE name = ? AND phone_number = ? AND address = ? ORDER BY id DESC LIMIT 1", (name, phone_number, address))
        store_id = cur.fetchone()
        return store_id[0]



if __name__ == "__main__":
    main()
