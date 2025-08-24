# CAPSタイプ診断アプリ - デプロイ手順

## Streamlit Cloud でのデプロイ（推奨）

### 1. GitHubリポジトリの準備
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/caps-diagnosis-app.git
git push -u origin main
```

### 2. Streamlit Cloudでデプロイ
1. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
2. GitHubアカウントでログイン
3. "New app" をクリック
4. リポジトリを選択
5. メインファイル: `caps_diagnosis_app.py`
6. "Deploy!" をクリック

## Heroku でのデプロイ

### 1. Heroku CLIのインストール
```bash
# macOS
brew tap heroku/brew && brew install heroku

# または公式サイトからダウンロード
```

### 2. Herokuアプリの作成とデプロイ
```bash
heroku login
heroku create your-app-name
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## ローカルでの動作確認
```bash
# 仮想環境をアクティベート
source venv/bin/activate

# アプリケーション実行
streamlit run caps_diagnosis_app.py
```

## 必要なファイル
- `caps_diagnosis_app.py` - メインアプリケーション
- `test_texts.csv` - 質問データ
- `requirements.txt` - 依存関係
- `Procfile` - Heroku用（Herokuデプロイ時のみ）
- `.streamlit/config.toml` - Streamlit設定

## 注意事項
- CSVファイルが正しく読み込まれることを確認
- 全ての依存関係がrequirements.txtに記載されていることを確認
- デプロイ後は本番URLでテストを実施
