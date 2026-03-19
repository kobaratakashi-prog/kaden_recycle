import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import io

# --- 1. アプリの設定 ---
st.set_page_config(page_title="家電リサイクル査定くん", layout="wide")
st.title("📱 家電リサイクル査定くん (2026.2確定版)")
st.write("写真をアップロードして「査定開始」を押してください。")

# 魔法の鍵を読み込み
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# --- 2. AIへの指示書（ここが精度の肝です） ---
SYSTEM_PROMPT = """
あなたは家電リサイクル査定のプロです。
写真から製品情報を抽出し、Google検索で「RKC 2026年2月版 料金表」を確認して、正確なコードと料金を特定してください。

【出力の絶対ルール】
1. Markdownの表（| や --- など）は絶対に、一切、使わないでください。
2. 項目と項目の間は、必ず「タブ文字」1つで区切ってください。
3. 余計な説明（「解析結果です」など）は一切書かず、データ行のみを出力してください。
4. 1行目は必ず以下の項目名（タブ区切り）にしてください。
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
        
        # モデルの設定（エラーが出にくい設定に変更）
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            tools=[{'google_search_retrieval': {}}]
        )

        for i, file in enumerate(uploaded_files):
            st.write(f"🔍 {file.name} を解析中...")
            img = Image.open(file)
            
            try:
                # 解析実行
                response = model.generate_content([SYSTEM_PROMPT, img])
                # 不要な記号を徹底的に掃除
                clean_text = response.text.replace("```text", "").replace("```", "").replace("|", "").strip()
                # ヘッダーが重複して出てきた場合は削除
                if "カテゴリ" in clean_text and i > 0:
                    clean_text = "\n".join(clean_text.split("\n")[1:])
                
                all_rows.append(clean_text)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        # --- 4. 結果表示 ---
        st.success("完了しました！")
        final_output = "\n".join(all_rows)
        
        # 視覚的な確認用の表（Excelっぽく見せる）
        st.subheader("📊 プレビュー")
        try:
            df = pd.read_csv(io.StringIO(final_output), sep='\t')
            st.dataframe(df, use_container_width=True)
        except:
            st.text("プレビューの作成に失敗しましたが、下のテキストはコピー可能です。")

        # Excel貼り付け用エリア
        st.subheader("📋 Excel貼り付け用テキスト")
        st.text_area("下の枠内を全選択（Ctrl+A）してコピーし、ExcelのA1セルに貼り付けてください。", final_output, height=300)
        
        st.download_button(label="ファイルを保存", data=final_output, file_name="recycle_data.txt")
