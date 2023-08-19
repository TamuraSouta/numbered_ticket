import streamlit as st
import pandas as pd
import requests
import urllib 

from db_utils import authenticate_user,add_user,get_store_info,issue_ticket,get_previous_ticket,check_store_exists
from config import GSI_API_BASE_URL


#ログイン画面
def display_login_page():
    # URLからstore_idを取得
    params = st.experimental_get_query_params()
    store_id = params.get("store_id", [None])[0]
    if not store_id or not check_store_exists(store_id):
        st.warning("そのURLは有効ではありません。")
        return  # 以降のログイン処理を中止
    
    st.subheader("ログイン")
    username = st.text_input("ユーザー名", key="client_username")
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

if 'error_message' not in st.session_state:
    st.session_state.error_message = ""
    
#新規登録画面
def display_register_page():
    st.subheader("新規登録")

    # セッション状態のエラーメッセージが初期化されていない場合は初期化します。
    if 'error_message' not in st.session_state:
        st.session_state.error_message = ""
    
    new_username = st.text_input("ユーザー名")
    new_password = st.text_input("パスワード", type='password')
    confirm_password = st.text_input("パスワード（再確認）", type='password')
    gender = st.selectbox("性別", ["男性", "女性", "その他"])  
    age = st.number_input("年齢", min_value=1, max_value=100)  
    email = st.text_input("メールアドレス") 
    
    if st.button("登録"):
        if not new_username or not new_password or not email:
            st.session_state.error_message = "すべての項目を入力してください。"
        elif new_password != confirm_password:
            st.session_state.error_message = "パスワードが一致しません。"
        elif "@" not in email:
            st.session_state.error_message = "有効なメールアドレスを入力してください。"
        else:
            st.session_state.registration_info = {
                "username": new_username,
                "password": new_password,
                "email": email,
                "gender": gender,
                "age": age
            }
            st.session_state.page = 'confirmation'
            st.session_state.error_message = ""
            st.experimental_rerun()  
        st.experimental_rerun()
    if st.session_state.error_message:
        st.warning(st.session_state.error_message)

# 内容確認ページ
def display_confirmation_page():
    st.subheader("内容確認")

    new_username = st.session_state.registration_info['username']
    new_password = st.session_state.registration_info['password']
    email = st.session_state.registration_info['email']
    gender = st.session_state.registration_info['gender']
    age = st.session_state.registration_info['age']
    
    st.write("以下の内容で登録します。よろしいですか？")
    st.write(f"ユーザー名: {new_username}")
    st.write(f"メールアドレス: {email}")
    st.write(f"性別: {gender}")
    st.write(f"年齢: {age}")
    
    if st.button("登録する"):
        if add_user(new_username,new_password,gender,age,email):
            st.session_state.page = 'login'  
            st.experimental_rerun() 
        else:
            st.warning("そのユーザー名は既に存在します。")

    if st.button("修正する"): 
        st.session_state.page = 'register'
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
        ticket_num, issued_num_people = issue_ticket(st.session_state.username, num_people, st.session_state.store_id)  # store_idを渡す
        st.session_state.ticket_num = ticket_num
        st.session_state.issued_num_people = issued_num_people

        if num_people > 100:
            st.warning("人数は100までです。")
            return
        st.session_state.page = 'show_ticket'
        st.experimental_rerun()
    if st.button("戻る"):
        st.session_state.page = 'main'
        st.experimental_rerun() 



#発行券確認画面 
def display_ticket_show_page():
    st.subheader("発行された整理券の情報")
    ticket_info = get_previous_ticket(st.session_state.username, st.session_state.store_id)  # store_idを追加
    if ticket_info:
        st.write(f"整理券番号: {ticket_info[0]}")
        st.write(f"人数: {ticket_info[1]}")
        
        # お店の情報を取得
        store_info = get_store_info(ticket_info[2])
        if store_info:
            address = store_info[2]
            st.write(f"電話番号: {store_info[1]}")
            st.write(f"住所: {address}")
            

            s_quote = urllib.parse.quote(address)
            response = requests.get(GSI_API_BASE_URL + s_quote)
            coordinates = response.json()[0]["geometry"]["coordinates"]
            data = pd.DataFrame({ 
                'lat': [coordinates[1]],  # 緯度と経度の順番を修正
                'lon': [coordinates[0]]
            }, index=[1])
            ## データを使用して地図を作成する
            if data:
                st.map(data)

            if st.button("戻る"):
                st.session_state.page = 'main'
                st.experimental_rerun() 
    else:
        st.write("まだ整理券は発行されていまaせん。")
        if st.button("新規発行"):
            st.session_state.page = 'issue_ticket'
            st.experimental_rerun()

