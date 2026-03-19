import streamlit as st
import google.generativeai as genai
import pandas as pd
from io import BytesIO

# --- 1. アプリの見た目の設定 ---
st.set_page_config(page_title="家電リサイクル査定くん", layout="wide")
st.title("📱 家電リサイクル査定くん (2026.2版)")
st.caption("写真をアップロードするだけで、最新のRKCデータと照合します。")

# --- 2. 魔法の鍵の入力設定 ---
# セキュリティのため、後で設定する「シークレット設定」から鍵を読み込みます
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# --- 3. AIへの「最強の指示書」 ---
SYSTEM_PROMPT = """
あなたは家電リサイクル査定の「ミス・ゼロ」を絶対条件とする専門家です。
写真から製品情報を抽出し、Google検索で「RKC 一般財団法人家電リサイクル券センター」の【2026年2月版 最新料金表】と厳密に照合して、Excel貼り付け用のデータを作成してください。

### 1. 精度維持の絶対ルール:
- 製造業者等名と略称は、必ずRKCの2026年2月版データと一文字の相違もなく一致させてください。
- コード（製造業者等名コード、品目・料金区分コード）および料金（税込）は、マスターデータと完全に一致していることを二重に確認してください。

### 2. カテゴリ・備考の出力ルール:
- カテゴリは [ テレビ / 冷蔵庫 / 冷凍庫 / 洗濯機 / エアコン ] から選択。
- 備考欄には、テレビなら「液晶・プラズマ/ブラウン管」と「型数」、冷蔵・冷凍庫なら「全定格内容積：〇〇L」を必ず記載してください。

### 3. 出力形式:
必ず以下の項目を、タブ区切り形式で出力してください。
通番 / カテゴリ / 製造業者等名 / 型番 / 製造業者等名の略称 / コード / 大小区分 / 品目・料金区分コード / リサイクル料金(税込) / 備考
"""

# --- 4. 画面の操作部分 ---
uploaded_files = st.file_uploader("製品ラベルの写真をアップロード（複数可）", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    if st.button("査定を開始する"):
        results = []
        progress_bar = st.progress(0)
        
        # AIモデルの準備 (Google検索機能付き)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={"temperature": 0},
            tools=[{'google_search_retrieval': {}}]
        )

        for i, file in enumerate(uploaded_files):
            st.write(f"🔍 {file.name} を解析中...")
            img = genai.Image.load_from_bytes(file.getvalue())
            
            # AIに解析を依頼
            response = model.generate_content([SYSTEM_PROMPT, img])
            results.append(response.text)
            progress_bar.progress((i + 1) / len(uploaded_files))

        # --- 5. 結果をきれいに表示 ---
        st.success("全ての解析が完了しました！")
        
        # 簡易的な表形式に変換して表示
        # (ここではユーザーがExcelに貼り付けやすい形式で画面に出します)
        all_text = "\n".join(results)
        st.code(all_text, language="text")
        
        # Excelダウンロードボタンの作成
        st.download_button(
            label="結果をテキストファイルで保存（Excel用）",
            data=all_text,
            file_name="recycle_check.txt",
            mime="text/plain"
        )
