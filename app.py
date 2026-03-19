import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import io

# --- 1. アプリの設定 ---
st.set_page_config(page_title="家電リサイクル査定くん", layout="wide")
st.title("📱 家電リサイクル査定くん (2026.2 本格Excel版)")

# 魔法の鍵を読み込み
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# --- 2. AIへの指示書 ---
SYSTEM_PROMPT = """
あなたは家電リサイクル査定のプロです。
写真から製品情報を抽出し、正確な料金区分を特定してください。
【出力形式】
以下の項目を「カンマ区切り」でデータのみ1行で出力してください。
通番, カテゴリ, 製造業者等名, 型番, 製造業者等名の略称, コード, 大小区分, 品目・料金区分コード, リサイクル料金(税込), 備考
"""

# --- 3. 操作画面 ---
uploaded_files = st.file_uploader("写真をアップロード（複数可）", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("査定を開始する"):
        all_data = []
        progress_bar = st.progress(0)
        
        # 【修正ポイント】モデル名を「models/gemini-1.5-flash」に固定
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        for i, file in enumerate(uploaded_files):
            st.write(f"🔍 {i+1}枚目: {file.name} を解析中...")
            img = Image.open(file)
            
            try:
                # 解析実行
                response = model.generate_content([SYSTEM_PROMPT, img])
                text = response.text.strip().replace("```csv", "").replace("```", "")
                
                for line in text.split("\n"):
                    parts = line.split(",")
                    if len(parts) >= 8 and "カテゴリ" not in line:
                        row = [item.strip() for item in parts]
                        row[0] = i + 1
                        all_data.append(row)
            except Exception as e:
                st.error(f"解析エラー: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        if all_data:
            st.success("全ての解析が完了しました！")
            columns = ["通番", "カテゴリ", "製造業者等名", "型番", "製造業者等名の略称", "コード", "大小区分", "品目・料金区分コード", "リサイクル料金(税込)", "備考"]
            df = pd.DataFrame(all_data, columns=columns)
            st.dataframe(df, use_container_width=True)

            # Excelファイル作成
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='査定リスト')
            
            st.download_button(
                label="Excelファイルをダウンロードする",
                data=buffer.getvalue(),
                file_name="家電リサイクル査定リスト_2026.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
