import streamlit as st
import pandas as pd
import numpy as np

def load_questions():
    """CSVファイルから質問とルールを読み込む"""
    import os
    # 現在のスクリプトと同じディレクトリのCSVファイルを読み込み
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'test_texts.csv')
    
    df = pd.read_csv(csv_path, sep='\t', header=None, names=['question', 'rule'])
    return df

def calculate_score(answer, rule):
    """回答とルールに基づいてスコアを計算する"""
    scores = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
    
    # 複合ルールを先に処理（より具体的なルールから）
    if '３から出た数を引いた数をaに足し、かつ出た数をdに足す' in rule:
        scores['a'] += (3 - answer)
        scores['d'] += answer
    elif '３から出た数を引いた数をcに足し、かつ出た数をbに足す' in rule:
        scores['c'] += (3 - answer)
        scores['b'] += answer
    elif '３から出た数を引いた数をbに足し、かつ出た数をcに足す' in rule:
        scores['b'] += (3 - answer)
        scores['c'] += answer
    elif '３から出た数を引いた数をdに足す' in rule:
        scores['d'] += (3 - answer)
    # 2倍ルール
    elif '出た数を2倍してaに足す' in rule:
        scores['a'] += answer * 2
    elif '出た数を2倍してbに足す' in rule:
        scores['b'] += answer * 2
    elif '出た数を2倍してcに足す' in rule:
        scores['c'] += answer * 2
    elif '出た数を2倍してdに足す' in rule:
        scores['d'] += answer * 2
    # 基本ルール
    elif '出た数をaに足す' in rule:
        scores['a'] += answer
    elif '出た数をbに足す' in rule:
        scores['b'] += answer
    elif '出た数をcに足す' in rule:
        scores['c'] += answer
    elif '出た数をdに足す' in rule:
        scores['d'] += answer
    
    return scores

def main():
    st.title("CAPSタイプ診断アプリケーション")
    st.write("各質問に対して0〜3の数字で回答してください。")
    
    # 質問データを読み込み
    try:
        questions_df = load_questions()
    except FileNotFoundError:
        st.error("test_texts.csvファイルが見つかりません。")
        return
    
    # セッション状態の初期化
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    
    # 質問表示と回答入力
    st.subheader("質問項目")
    
    # 回答の説明を追加
    st.markdown("""
    **回答の基準:**  
    0 = あてはまらない　1 = どちらかといえばあてはまらない　2 = どちらかといえばあてはまる　3 = あてはまる
    """)
    st.markdown("---")
    
    # 全ての質問を1ページで表示
    for i, row in questions_df.iterrows():
        question_num = i + 1
        question_text = row['question']
        
        # 質問文をそのまま表示（番号は既に含まれている）
        st.write(f"**{question_text}**")
        
        # 回答選択（初期値なし、未選択状態）
        if question_num in st.session_state.answers:
            # 既に回答済みの場合は、その値をデフォルトに
            default_index = st.session_state.answers[question_num]
        else:
            # 未回答の場合はNoneを設定（未選択状態）
            default_index = None
        
        answer = st.radio(
            f"質問{question_num}の回答",
            options=[0, 1, 2, 3],
            key=f"q_{question_num}",
            index=default_index,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # 回答が選択された場合のみセッション状態を更新
        if answer is not None:
            st.session_state.answers[question_num] = answer
        
        st.write("---")
    
    # 全ての質問に回答済みの場合、結果を計算・表示
    total_questions = len(questions_df)
    answered_questions = len(st.session_state.answers)
    
    if answered_questions == total_questions:
        st.subheader("診断結果")
        
        # スコア計算
        total_scores = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
        
        # デバッグ情報を表示するかどうかのチェックボックス
        show_debug = st.checkbox("詳細な計算過程を表示", value=False)
        
        if show_debug:
            st.subheader("計算過程の詳細")
            debug_data = []
        
        for i, row in questions_df.iterrows():
            question_num = i + 1
            answer = st.session_state.answers[question_num]
            rule = row['rule']
            
            scores = calculate_score(answer, rule)
            
            if show_debug:
                debug_data.append({
                    '質問番号': question_num,
                    '回答': answer,
                    'ルール': rule,
                    'a加点': scores['a'],
                    'b加点': scores['b'],
                    'c加点': scores['c'],
                    'd加点': scores['d']
                })
            
            for key in total_scores:
                total_scores[key] += scores[key]
        
        if show_debug:
            debug_df = pd.DataFrame(debug_data)
            st.dataframe(debug_df, use_container_width=True)
        
        # 結果表示
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("コントローラー (C)", total_scores['a'])
            st.metric("アナライザー (A)", total_scores['b'])
        
        with col2:
            st.metric("プロモーター (P)", total_scores['c'])
            st.metric("サポーター (S)", total_scores['d'])
        
        # 最高スコアのタイプを判定
        max_score = max(total_scores.values())
        dominant_types = [k for k, v in total_scores.items() if v == max_score]
        
        type_names = {
            'a': 'コントローラー',
            'b': 'アナライザー', 
            'c': 'プロモーター',
            'd': 'サポーター'
        }
        
        if len(dominant_types) == 1:
            st.success(f"あなたの主要タイプは **{type_names[dominant_types[0]]}** です！")
        else:
            dominant_type_names = [type_names[t] for t in dominant_types]
            st.info(f"あなたは複数のタイプの特徴を持っています: **{', '.join(dominant_type_names)}**")
        
        # グラフ表示
        st.subheader("スコア分布")
        chart_data = pd.DataFrame({
            'タイプ': ['コントローラー', 'アナライザー', 'プロモーター', 'サポーター'],
            'スコア': [total_scores['a'], total_scores['b'], total_scores['c'], total_scores['d']]
        })
        st.bar_chart(chart_data.set_index('タイプ'))
        
        # タイプ説明をタブで表示
        st.subheader("各タイプの詳細説明")
        tab1, tab2, tab3, tab4 = st.tabs(["コントローラー", "アナライザー", "プロモーター", "サポーター"])
        
        with tab1:
            st.markdown("""
            ### コントローラー（Controller）
            
            **特徴:**
            - リーダーシップを発揮し、目標達成に向けて積極的に行動する
            - 決断力があり、責任感が強い
            - 効率性を重視し、結果を出すことにこだわる
            - 競争心が強く、挑戦を好む
            
            **強み:**
            - 迅速な意思決定ができる
            - 困難な状況でもリーダーシップを発揮
            - 目標達成への強い意志
            - 変化に対する適応力
            
            **注意点:**
            - 他者の意見を聞かずに独断で進めがち
            - せっかちで、他者のペースに合わせるのが苦手
            - 完璧主義になりすぎることがある
            
            **適した役割:**
            - チームリーダー、プロジェクトマネージャー
            - 営業職、起業家
            - 危機管理責任者
            """)
        
        with tab2:
            st.markdown("""
            ### アナライザー（Analyzer）
            
            **特徴:**
            - 論理的思考を重視し、慎重に分析してから行動する
            - データや事実に基づいて判断する
            - 完璧性を求め、品質にこだわる
            - 計画性があり、リスクを事前に検討する
            
            **強み:**
            - 正確性と品質の高い成果物を作成
            - 論理的で客観的な判断ができる
            - 問題の本質を見抜く分析力
            - 長期的な視点での計画立案
            
            **注意点:**
            - 決断に時間がかかりすぎることがある
            - 完璧を求めすぎて行動が遅れがち
            - 感情的なコミュニケーションが苦手
            
            **適した役割:**
            - 研究職、エンジニア
            - 財務・経理担当
            - 品質管理、監査
            - データアナリスト
            """)
        
        with tab3:
            st.markdown("""
            ### プロモーター（Promoter）
            
            **特徴:**
            - 社交的で楽観的、新しいアイデアや変化を好む
            - コミュニケーション能力が高く、人を巻き込むのが得意
            - 創造性豊かで、革新的なアイデアを生み出す
            - エネルギッシュで、周囲を明るくする
            
            **強み:**
            - 優れたコミュニケーション能力
            - 創造性と革新性
            - チームの士気を高める能力
            - 変化への柔軟な対応
            
            **注意点:**
            - 細かい作業や継続的な業務が苦手
            - 計画性に欠けることがある
            - 飽きやすく、集中力が続かない場合がある
            
            **適した役割:**
            - 営業・マーケティング
            - 企画・開発
            - 広報・PR
            - イベントプランナー
            """)
        
        with tab4:
            st.markdown("""
            ### サポーター（Supporter）
            
            **特徴:**
            - 協調性を重視し、他者をサポートすることを大切にする
            - 安定性を好み、調和のとれた環境を求める
            - 忍耐強く、継続的な努力ができる
            - 他者の気持ちを理解し、共感する能力が高い
            
            **強み:**
            - 優れたチームワーク
            - 継続性と安定性
            - 他者への共感と支援能力
            - 調整役としての能力
            
            **注意点:**
            - 自己主張が苦手で、意見を言いにくい
            - 変化に対して慎重すぎることがある
            - 他者を優先しすぎて自分を犠牲にしがち
            
            **適した役割:**
            - 人事・総務
            - カスタマーサポート
            - 教育・研修
            - チームのサポート役
            """)
        
        # リセットボタン
        if st.button("診断をやり直す"):
            st.session_state.answers = {}
            st.rerun()
    
    else:
        remaining = total_questions - answered_questions
        if remaining > 0:
            st.info(f"残り {remaining} 問の質問に回答してください。")
        
        # 進捗表示
        if answered_questions > 0:
            progress = answered_questions / total_questions
            st.progress(progress)
            st.write(f"回答済み: {answered_questions}/{total_questions}")
    
    # 管理者情報を最下部に表示
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 2rem;'>"
        "医事課　古川が管理者研修の内容を踏まえて個人作成したアプリです。要望あれば古川までお願いします。"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
