from db_utils import init_db
from views.client_side import display_login_page ,display_register_page ,display_ticket_issue_page,display_ticket_show_page,display_main_page,display_store_register_page,display_confirmation_page
import streamlit as st
import pandas as pd





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
    elif st.session_state.page == 'confirmation':
        display_confirmation_page()
    elif st.session_state.page == 'issue_ticket':
        display_ticket_issue_page()
    elif st.session_state.page == 'show_ticket':
        display_ticket_show_page()
    elif st.session_state.page == 'main':
        display_main_page() 
    elif st.session_state.page == 'store_register': 
        display_store_register_page()


if __name__ == "__main__":
    main()