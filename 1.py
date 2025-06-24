import streamlit as st
import pandas as pd
from janome.tokenizer import Tokenizer
import random

# ハードル練習メニューCSV読み込み
df = pd.read_csv("hurdle_data_for_streamlit.csv")

# タイトル
st.title("110mハードル練習メニュー提案システム")

# 入力フォーム
age = st.number_input("あなたの年齢を入力してください", min_value=10, max_value=100, value=15)
experience = st.number_input("競技歴（年数）を入力してください", min_value=0, max_value=20, value=2)
goal_input = st.text_input("上達したいことを入力してください（例：スピード強化、フォーム改善 など）")

if st.button("メニューを提案！") and goal_input:
    # 形態素解析
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(goal_input, wakati=False)
    keywords = [token.surface for token in tokens if "名詞" in token.part_of_speech]

    # 経験年数による割合決定（仮の分類）
    if experience <= 2:
        ratio = {'ウォーミングアップ・モビリティ向上': 0.3, '基礎技術（リズム・動作の習得）': 0.3, '専門技術（ハードル練習）': 0.4}
    elif 3 <= experience <= 5:
        ratio = {'専門技術（ハードル練習）': 0.4, 'スプリント強化': 0.3, '筋力強化': 0.3}
    else:
        ratio = {'スプリント強化': 0.4, '筋力強化': 0.3, '専門技術（ハードル練習）': 0.3}

    # キーワードによるフィルタリング
    filtered_df = pd.DataFrame()
    for kw in keywords:
        filtered_df = pd.concat([filtered_df, df[df["得られる効果"].str.contains(kw, na=False)]])
    filtered_df = filtered_df.drop_duplicates()
    filtered_df = filtered_df[filtered_df["適切な年齢"] <= age]

    # 種類ごとに抽出
    final_output = pd.DataFrame()
    for t_type, r in ratio.items():
        subset = filtered_df[filtered_df["種類"] == t_type]
        n_samples = max(1, int(len(filtered_df) * r))
        final_output = pd.concat([final_output, subset.sample(n=min(n_samples, len(subset)), random_state=42)])

    # 出力
    if not final_output.empty:
        st.subheader(f"🎯 競技歴{experience}年のあなたにおすすめのハードル練習メニュー")
        for _, row in final_output.iterrows():
            st.markdown(f"### ● メニュー名：{row['メニュー名']}")
            st.write(f"・説明：{row['メニューの説明']}")
            st.write(f"・効果：{row['得られる効果']}")
            st.write(f"・形式：{row['種類']}")
            st.write(f"・推奨年齢：{row['適切な年齢']}歳以上")
            st.markdown("---")
    else:
        st.warning("該当するメニューが見つかりませんでした。入力内容を見直してください。")
