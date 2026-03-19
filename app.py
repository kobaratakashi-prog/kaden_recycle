import streamlit as st
import google.generativeai as genai

st.title("接続テスト")

# APIキーの読み込み
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

if st.button("接続できるかチェック"):
    try:
        # 使えるモデルの一覧を取得してみる
        models = [m.name for m in genai.list_models()]
        st.success("接続成功！")
        st.write("あなたが今使えるモデル一覧:")
        st.write(models)
    except Exception as e:
        st.error(f"接続に失敗しました。理由: {e}")
