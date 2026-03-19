import streamlit as st
import google.generativeai as genai
import pandas as pd
from PIL import Image
import io

# --- 1. アプリの設定 ---
st.set_page_config(page_title="家電リサイクル査定くん", layout="wide")
st.title("📱 家電リサイクル査定くん (2026.2版)")

# 魔法の鍵を読み込み
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# --- 2. AIへの指示書（Excel貼り付けに特化） ---
SYSTEM_PROMPT = """
あなたは家電リサイクル査定の専門家です。
写真から製品情報を抽出し、Google検索で「RKC 一般財団法人家電リサイクル券センター」の【2026年2月版 最新料金表】と照合してください。

### 【重要】出力形式のルール:
- 結果は必ず「タブ区切り」の形式で出力してください。
- Markdownの表（ | で区切る形式）は絶対に禁止です。
- 1行目は必ず以下のヘッダーにしてください。
通番	カテゴリ	製造業者等名	型番	製造業者等名の略称	コード	大小区分	品目・料金区分コード	リサイクル料金(税込)	備考

### 判定ルール:
- カテゴリは [ テレビ / 冷蔵庫 / 冷凍庫 / 洗濯機 / エアコン ] から選択。
- 備考欄には、テレビなら「液晶・プラズマ/ブラウン管」と「型数」、冷蔵・冷凍庫なら「全定格内容積：〇〇L」を記載。
- 略称・コード・料金は、RKCの2026年2月版データと一文字も違わず一致させてください。
"""

# --- 3. 操作画面 ---
uploaded_files = st.file_uploader("写真をアップロード", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("査定を開始する"):
        all_results = []
        progress_bar = st.progress(0)
        
        # モデルの準備
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            tools=[{'google_search_retrieval': {}}]
        )

        for i, file in enumerate(uploaded_files):
            st.write(f"🔍 {file.name} を解析中...")
            
            # 【修正点】画像読み込みをPillowに変更
            img = Image.open(file)
            
            # AIに依頼
            response = model.generate_content([SYSTEM_PROMPT, img])
            
            # 結果を整理（余計な文字を削除）
            clean_text = response.text.replace("```text", "").replace("```", "").strip()
            all_results.append(clean_text)
            
            progress_bar.progress((i + 1) / len(uploaded_files))

        # --- 4. 結果表示 ---
        st.success("完了しました！")
        
        # 画面に表示
        final_output = "\n".join(all_results)
        st.text_area("Excel貼り付け用データ（これをコピーしてExcelのA1に貼ってください）", final_output, height=300)
        
        # ダウンロードボタン
        st.download_button(
            label="ファイルを保存",
            data=final_output,
            file_name="recycle_data.txt",
            mime="text/plain"
        )
