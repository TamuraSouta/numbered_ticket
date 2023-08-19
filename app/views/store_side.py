import streamlit as st
from db_utils import authenticate_store,register_store,check_store_exists
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
            st.session_state.page = 'store_dashboard'
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

def display_store_dashboard_page():
    if st.button("戻る"):
            st.session_state.page = 'login'
            st.experimental_rerun() 