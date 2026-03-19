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

# --- 2. AIへの指示書（より厳密に） ---
SYSTEM_PROMPT = """
あなたは家電リサイクル査定のプロです。
写真から製品情報を抽出し、Google検索で「RKC 2026年2月版 料金表」を確認して、正確なコードと料金を特定してください。

【出力形式】
以下の項目を「カンマ区切り（CSV形式）」で、データのみを1行で出力してください。
通番, カテゴリ, 製造業者等名, 型番, 製造業者等名の略称, コード, 大小区分, 品目・料金区分コード, リサイクル料金(税込), 備考
"""

# --- 3. 操作画面 ---
uploaded_files = st.file_uploader("写真をアップロード（複数可）", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("査定を開始する"):
        all_data = []
        progress_bar = st.progress(0)
        
        # エラーが出にくいモデル指定に変更
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[{'google_search_retrieval': {}}]
        )

        for i, file in enumerate(uploaded_files):
            st.write(f"🔍 {i+1}枚目: {file.name} を解析中...")
            img = Image.open(file)
            
            try:
                # 解析実行
                response = model.generate_content([SYSTEM_PROMPT, img])
                text = response.text.strip().replace("```csv", "").replace("```", "").replace("|", ",")
                
                # 行を分割して整理
                for line in text.split("\n"):
                    if "カテゴリ" not in line and len(line.split(",")) > 5:
                        row = [item.strip() for item in line.split(",")]
                        # 通番を上書き
                        row[0] = i + 1
                        all_data.append(row)
            except Exception as e:
                st.error(f"解析エラー: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        # --- 4. 結果表示とExcel保存 ---
        if all_data:
            st.success("全ての解析が完了しました！")
            
            # データを表に変換
            columns = ["通番", "カテゴリ", "製造業者等名", "型番", "製造業者等名の略称", "コード", "大小区分", "品目・料金区分コード", "リサイクル料金(税込)", "備考"]
            df = pd.DataFrame(all_data, columns=columns)
            
            # 画面にプレビューを表示
            st.subheader("📊 解析結果プレビュー")
            st.dataframe(df, use_container_width=True)

            # --- Excelファイルを作成（ここが新機能！） ---
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='査定リスト')
            
            st.subheader("💾 保存")
            st.download_button(
                label="Excelファイルをダウンロードする",
                data=buffer.getvalue(),
                file_name="家電リサイクル査定リスト_2026.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("解析データが取得できませんでした。もう一度お試しください。")import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import io

# --- 1. アプリの設定 ---
st.set_page_config(page_title="家電リサイクル査定くん", layout="wide")
st.title("📱 家電リサイクル査定くん (2026.2 確定版)")
st.write("写真をアップロードして「査定開始」を押してください。")

# 魔法の鍵を読み込み
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# --- 2. AIへの指示書 ---
SYSTEM_PROMPT = """
あなたは家電リサイクル査定のプロです。
写真から製品情報を抽出し、Google検索で「RKC 2026年2月版 料金表」を確認して、正確なコードと料金を特定してください。

【出力の絶対ルール】
1. 棒線（|）やアスタリスク（*）などの飾りは絶対に一切使わないでください。
2. 項目と項目の間は、必ず「タブ文字（Tab）」1つで区切ってください。
3. 1行目は必ず以下のヘッダー（タブ区切り）にしてください。
通番	カテゴリ	製造業者等名	型番	製造業者等名の略称	コード	大小区分	品目・料金区分コード	リサイクル料金(税込)	備考
"""

# --- 3. 操作画面 ---
uploaded_files = st.file_uploader("写真をアップロード（複数可）", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("査定を開始する"):
        all_rows = []
        # ヘッダーを最初に入れる
        header = "通番	カテゴリ	製造業者等名	型番	製造業者等名の略称	コード	大小区分	品目・料金区分コード	リサイクル料金(税込)	備考"
        all_rows.append(header)
        
        progress_bar = st.progress(0)
        
        # モデルの設定（エラーが出にくい名称に変更）
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", # より安定しているFlash版に変更
            tools=[{'google_search_retrieval': {}}]
        )

        for i, file in enumerate(uploaded_files):
            st.write(f"🔍 {file.name} を解析中...")
            img = Image.open(file)
            
            try:
                # 解析実行
                response = model.generate_content([SYSTEM_PROMPT, img])
                # 余計な記号を徹底的に掃除
                clean_text = response.text.replace("```text", "").replace("```", "").replace("|", "").strip()
                # ヘッダーが重複して出てきた場合は削除
                if "カテゴリ" in clean_text:
                    lines = clean_text.split("\n")
                    clean_text = "\n".join([l for l in lines if "カテゴリ" not in l and l.strip()])
                
                if clean_text:
                    all_rows.append(clean_text)
            except Exception as e:
                st.error(f"解析エラー: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        # --- 4. 結果表示 ---
        st.success("完了しました！")
        final_output = "\n".join(all_rows)
        
        # Excel貼り付け用エリア（ここが一番大事です）
        st.subheader("📋 Excel貼り付け用テキスト")
        st.info("下の枠内をマウスでなぞってコピーし、ExcelのA1セルに貼り付けてください。")
        st.text_area("（コピー用）", final_output, height=300)
        
        # プレビュー表
        st.subheader("📊 プレビュー")
        try:
            df = pd.read_csv(io.StringIO(final_output), sep='\t')
            st.dataframe(df, use_container_width=True)
        except:
            st.write("（プレビューは作成中ですが、上のテキストはコピー可能です）")

        st.download_button(label="ファイルをダウンロード", data=final_output, file_name="recycle_data.txt")
