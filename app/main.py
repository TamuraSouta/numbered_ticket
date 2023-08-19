from db_utils import init_db
from views.client_side import display_login_page as client_login_page  ,display_register_page ,display_ticket_issue_page,display_ticket_show_page,display_main_page,display_confirmation_page
from views.store_side import display_login_page as store_login_page , display_store_register_page,display_store_dashboard_page
import streamlit as st
import pandas as pd


# セッション状態の初期設定
if 'page' not in st.session_state:
    st.session_state.page = 'login' # 最初に開くページの設定
    st.session_state.store_id = 1  # デフォルトの店のIDを設定
    st.session_state.role = 'customer'  # Default role

def main():
    # クエリパラメータから店のIDと役割（ロール）を取得
    params = st.experimental_get_query_params()
    
    # store_idの取得
    store_id_from_url = params.get("store_id")
    if store_id_from_url:
        st.session_state.store_id = int(store_id_from_url[0])
    
    # roleの取得
    role_from_url = params.get("role")
    if role_from_url:
        st.session_state.role = role_from_url[0]

    init_db()
    
    ## 客側 ##
    if st.session_state.role == 'customer':
        if st.session_state.page == 'login':
            client_login_page()
        elif st.session_state.page == 'register':
            display_register_page()
        elif st.session_state.page == 'confirmation':
            display_confirmation_page()
        elif st.session_state.page == 'issue_ticket':
            display_ticket_issue_page()
        elif st.session_state.page == 'show_ticket':
            display_ticket_show_page()
        elif st.session_state.page == 'main':
            display_main_page() 

    ## 店側 ##
    elif st.session_state.role == 'store':
        if st.session_state.page == 'login':
            store_login_page()
        elif st.session_state.page == "store_registration":
            display_store_register_page()
        elif st.session_state.page == "store_dashboard":
            display_store_dashboard_page()

if __name__ == "__main__":
    main()