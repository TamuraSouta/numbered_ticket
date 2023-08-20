import streamlit as st
import pandas as pd
from db_utils import authenticate_store,register_store,check_store_exists,get_store_info,fetch_ticket_info
from config import ADMIN_ID,ADMIN_PASSWORD


# ログイン画面
def display_login_page():
    st.subheader("店側ログイン")
    
    store_id = st.text_input("店ID") 
    password = st.text_input("パスワード", type='password')

    if st.button("ログイン"):
        if store_id == ADMIN_ID and password == ADMIN_PASSWORD:
            st.session_state.page = 'store_registration'
            st.experimental_rerun()
        elif authenticate_store(store_id, password):
            st.session_state.store_id = store_id
            st.session_state.page = 'store_main'
            st.experimental_rerun() 
        else:
            st.warning("認証に失敗しました。もう一度試してください。")

# お店登録画面
def display_store_register_page():
    st.subheader("お店の登録")
    
    store_name = st.text_input("店名")
    store_id = st.text_input("店ID")
    password = st.text_input("パスワード", type='password')
    confirm_password = st.text_input("パスワード（再確認）", type='password')
    phone_number = st.text_input("電話番号")
    email = st.text_input("メールアドレス")
    address = st.text_input("住所")
    if 'error_message' in st.session_state and st.session_state.error_message:
        st.error(st.session_state.error_message)
        del st.session_state.error_message 

    if st.button("お店を登録"):
        if not store_id or not store_name or not password or not phone_number or not email or not address:
            st.session_state.error_message = "すべての項目を入力してください。"
        elif password != confirm_password:
            st.session_state.error_message = "パスワードが一致しません。"
        elif "@" not in email:
            st.session_state.error_message = "有効なメールアドレスを入力してください。"
        elif check_store_exists(store_id):
            st.session_state.error_message = "idが存在しています"
        else:
            register_store(store_id,store_name, password, phone_number, email,address)  
            st.session_state.page = 'login'
            st.experimental_rerun()
    if st.button("戻る"):
            st.session_state.page = 'login'
            st.experimental_rerun() 

# メイン画面
def display_store_main_page():
    st.subheader("お店のメイン画面")
    
    # お店の情報を取得する
    store_info = get_store_info(st.session_state.store_id)
    if store_info:
        st.write(f"お店の名前: {store_info[0]}")  # お店の名前を表示
    
    # 整理券制御ページに遷移するボタン
    if st.button("整理券の制御"):
        st.session_state.page = 'ticket_control'
        st.experimental_rerun()

# 整理券制御ページ
def display_ticket_control_page():
    # 整理券情報を取得
    tickets = fetch_ticket_info(st.session_state.store_id)

    # 整理券情報をDataFrameに変換
    df = pd.DataFrame(tickets, columns=['整理券番号', 'ユーザー名', '人数'])

    # DataFrameを表示
    st.table(df)

    # 呼び出しボタンの表示と処理
    selected_ticket = st.selectbox("整理券を選択してください", df['整理券番号'].tolist())
    if st.button("呼び出し"):
        st.success(f"{selected_ticket}番のお客様を呼び出しました。")
        
    if st.button("メインページに戻る"):
        st.session_state.page = 'store_main'
        st.experimental_rerun()

