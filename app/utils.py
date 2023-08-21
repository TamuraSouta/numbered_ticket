import streamlit as st

def display_error_message(message):
    """エラー表示とページ更新"""
    st.session_state.error_message = message
    st.experimental_rerun()

def go_to_page(page_name):
    """ページ変数の変換とページ更新"""
    st.session_state.page = page_name
    st.experimental_rerun()

def display_error_if_exists():
    """セッションエラーの表示"""
    if 'error_message' in st.session_state and st.session_state.error_message:
        st.error(st.session_state.error_message)
        del st.session_state.error_message 
