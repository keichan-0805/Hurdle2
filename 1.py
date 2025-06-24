import streamlit as st
import pandas as pd
from janome.tokenizer import Tokenizer
import random

# ハードル練習メニューCSV読み込み
df = pd.read_csv("hurdle_data_for_streamlit.csv")

# タイトル
st.title("110mハードル練習メニュー（1週間）自動提案")

# 質問入力
goal_input = st.text_input("どんな課題を改善したいですか？（例：スタートが遅い、体幹が弱い など）")

if st.button("1週間分のメニューを作成！") and goal_input:
    # 形態素解析によるキーワード抽出
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize(goal_input, wakati=False)
    keywords = [token.surface for token in tokens if "名詞" in token.part_of_speech]

    # キーワードによるカテゴリフィルタ
    filtered_df = pd.DataFrame()
    for kw in keywords:
        filtered_df = pd.concat([filtered_df, df[df["得られる効果"].str.contains(kw, na=False)]])
    filtered_df = filtered_df.drop_duplicates()

    # データがないときの対処
    if filtered_df.empty:
        st.warning("該当するキーワードのメニューが見つかりませんでした。入力内容を変えてみてください。")
    else:
        # 強度のバランスを取って7日間メニューを構成（高:中:低 = 2:3:2）
        days = ["月", "火", "水", "木", "金", "土", "日"]
        weekly_plan = pd.DataFrame()

        # 強度レベル分け
        high = filtered_df[filtered_df["強度"] >= 4]
        mid = filtered_df[(filtered_df["強度"] == 3)]
        low = filtered_df[filtered_df["強度"] <= 2]

        schedule = []
        schedule += random.sample(list(high.index), min(2, len(high)))
        schedule += random.sample(list(mid.index), min(3, len(mid)))
        schedule += random.sample(list(low.index), min(2, len(low)))
        selected = filtered_df.loc[schedule].sample(n=min(7, len(schedule)), random_state=42)

        # 表示
        st.subheader("🗓 あなたにおすすめの1週間分の練習メニュー")

        for i, (_, row) in enumerate(selected.iterrows()):
            st.markdown(f"### {days[i]}曜日：{row['メニュー名']}")
            st.write(f"・説明：{row['メニューの説明']}")
            st.write(f"・効果：{row['得られる効果']}")
            st.write(f"・形式：{row['種類']}")
            st.write(f"・強度：{row['強度']}")
            st.markdown("---")
