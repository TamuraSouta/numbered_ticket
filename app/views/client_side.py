import streamlit as st
import pandas as pd
import requests
import urllib 

from utils import go_to_page,display_error_if_exists,display_error_message
from db_utils import authenticate_user,add_user,get_store_info,issue_ticket,get_previous_ticket,check_store_exists,cancel_ticket,user_has_ticket,user_exists,update_user_info
from config import GSI_API_BASE_URL

st.session_state.OPEN_STATUS = False

#ログイン画面
def display_login_page():
    # URLからstore_idを取得
    params = st.experimental_get_query_params()
    store_id = params.get("store_id", [None])[0]

    if check_store_exists(store_id):
        st.session_state.store_id = store_id 
        st.session_state.OPEN_STATUS = True 
    else:
        st.session_state.store_id = None
        st.warning("このurlでは整理券を発行することはできません")
    
    display_error_if_exists()

    st.subheader("ログイン")
    username = st.text_input("ユーザー名", key="client_username")
    password = st.text_input("パスワード", type='password')
    if st.button("ログイン"):
        if authenticate_user(username, password):
            st.session_state.username = username 
            go_to_page('main' )
        else:
            st.warning("ユーザー名またはパスワードが間違っています。")

    # 新規登録画面に遷移
    if st.button("新規登録画面へ"):
        go_to_page('register')


#新規登録画面
def display_register_page():
    st.subheader("新規登録")

    display_error_if_exists()
    
    new_username = st.text_input("ユーザー名")
    new_password = st.text_input("パスワード", type='password')
    confirm_password = st.text_input("パスワード（再確認）", type='password')
    gender = st.selectbox("性別", ["男性", "女性", "その他"])  
    age = st.number_input("年齢", min_value=1, max_value=100)  
    email = st.text_input("メールアドレス") 
    
    if st.button("登録"):
        if not new_username or not new_password or not email:
            display_error_message( "すべての項目を入力してください。")
        elif new_password != confirm_password:
            display_error_message( "パスワードが一致しません。")
        elif "@" not in email:
            display_error_message( "有効なメールアドレスを入力してください。")
        elif user_exists(new_username):
            display_error_message("そのユーザー名は既に存在します。")
        else:
            st.session_state.registration_info = {
                "username": new_username,
                "password": new_password,
                "email": email,
                "gender": gender,
                "age": age
            }
            go_to_page('confirmation')
        display_error_if_exists()
    if st.button("戻る"):
        go_to_page('login')

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
            go_to_page('login')
        else:
            display_error_message("そのユーザー名は既に存在します。")

    if st.button("修正する"): 
        go_to_page('register')
        st.experimental_rerun()

        
#メイン画面
def display_main_page():
    st.subheader("メイン画面")
    
    # OPEN_STATUS の初期化
    if 'OPEN_STATUS' not in st.session_state:
        st.session_state.OPEN_STATUS = False

    display_error_if_exists()

    store_info = get_store_info(st.session_state.store_id)
    if store_info:
        st.write(f"お店の名前: {store_info[0]}")  
    if st.button("発行番号の確認"):
        go_to_page('show_ticket')
    if st.session_state.OPEN_STATUS:
        if st.button("新規発行"):
            go_to_page('issue_ticket')
    if st.button("ユーザー情報を更新"):
        go_to_page('update_user_info')

#発行券発行画面
def display_ticket_issue_page():
    st.subheader("整理券発行")

    num_people = st.number_input("人数を入力してください", min_value=1, max_value=100, value=1)
    if st.button("整理券を発行"):
        if user_has_ticket(st.session_state.username):
            st.session_state.error_message = "すでに他の店舗で整理券を取得しています。 整理券をご確認ください"
            go_to_page('main')
            return
        else:
            ticket_num, issued_num_people = issue_ticket(st.session_state.username, num_people, st.session_state.store_id)  # store_idを渡す
            st.session_state.ticket_num = ticket_num
            st.session_state.issued_num_people = issued_num_people

            if num_people > 100:
                st.warning("人数は100までです。")
                return
            go_to_page('show_ticket')
            st.experimental_rerun()
    
    if st.button("戻る"):
        go_to_page('main')
        st.experimental_rerun() 

#発行券確認画面 
def display_ticket_show_page():
    st.subheader("発行された整理券の情報")
    ticket_info = get_previous_ticket(st.session_state.username)
    if ticket_info:
        if ticket_info[2] != st.session_state.store_id:
            st.warning("このお店の整理券ではありません")

        st.write(f"整理券番号: {ticket_info[0]}")
        st.write(f"店名: {ticket_info[3]}") 
        st.write(f"人数: {ticket_info[1]}")
        
        # 店の情報を表示
        store_info = get_store_info(ticket_info[2]) 
        if store_info:
            phone_number = store_info[1]
            address = store_info[2]
            st.write(f"電話番号: {phone_number}")
            st.write(f"住所: {address}")
            s_quote = urllib.parse.quote(address)
            response = requests.get(GSI_API_BASE_URL + s_quote)
            coordinates = response.json()[0]["geometry"]["coordinates"]
            data = pd.DataFrame({ 
                'lat': [coordinates[1]],  
                'lon': [coordinates[0]]
            }, index=[1])
            # データを使用して地図を作成する
            st.map(data)

            # キャンセル機能の実装
            if st.button("整理券のキャンセル"):
                cancel_ticket(st.session_state.username, st.session_state.store_id)  # 整理券をキャンセル
                go_to_page('main')
            
            if st.button("戻る"):
                go_to_page('main')

    elif st.session_state.OPEN_STATUS :
        st.write("まだ整理券は発行されていまません。")
        if st.button("新規発行"):
            go_to_page('issue_ticket')

def display_user_info_update_page():
    st.subheader("ユーザー情報の更新")
    current_username = st.session_state.username
    st.write("ユーザー名",current_username)

    password = st.text_input("新しいパスワード", type='password')
    confirm_password = st.text_input("新しいパスワード（再確認）", type='password')
    gender = st.selectbox("性別", ["男性", "女性", "その他"])  
    age = st.number_input("年齢", min_value=1, max_value=100)  
    email = st.text_input("メールアドレス") 

    if st.button("更新"):
        if password != confirm_password:
            st.warning("パスワードが一致しません。")
        else:
            update_user_info(current_username, password, gender, age, email)
            st.success("ユーザー情報が更新されました。")

    if st.button("戻る"):
        go_to_page('main')

