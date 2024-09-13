import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import datetime
from flask import Flask, Blueprint, request, jsonify

add_calender_bp = Blueprint('add_calender_bp', __name__)
@add_calender_bp.route('/add_calender', methods=['POST'])
def add_calender():
    form_data = request.json
    add_event_to_calendar(form_data['summary'], 
                          form_data['start_time'], 
                          form_data['end_time'], 
                          form_data['location'], 
                          form_data['description'])

def authenticate_google_calendar():
    """Google Calendar APIに認証して認証情報を返す"""
    
    # 環境変数からGoogle OAuth 2.0の設定情報を取得
    client_id = os.getenv('GCP_CLIENT_ID')
    client_secret = os.getenv('GCP_CLIENT_SECRET')
    
    # OAuth 2.0のクライアント設定を構成
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": [os.getenv('GCP_REDIRECT_URIS')]  # リダイレクトURIも必要に応じて設定
            }
        },
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    
    # 認証フローを開始し、トークンを取得
    creds = flow.run_local_server(port=8080)
    
    return creds

def add_event_to_calendar(creds, summary, start_time, end_time, location=None, description=None):
    """
    Google Calendarにイベントを追加する関数
    
    Args:
        creds: Google APIの認証情報
        summary (str): イベントのタイトル
        start_time (str): イベントの開始時間（ISOフォーマット）
        end_time (str): イベントの終了時間（ISOフォーマット）
        location (str): イベントの場所（オプション）
        description (str): イベントの説明（オプション）
    """
    # Google Calendar APIにアクセス
    service = build('calendar', 'v3', credentials=creds)
    
    # イベントの詳細を作成
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Asia/Tokyo',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Asia/Tokyo',
        }
    }
    
    # イベントをカレンダーに追加
    event_result = service.events().insert(calendarId='primary', body=event).execute()
    
    print(f"Event created: {event_result.get('htmlLink')}")

if __name__ == "__main__":
    # 認証処理
    creds = authenticate_google_calendar()
    
    # 外部から取得するイベントのパラメータ（例）
    event_summary = "会議"
    event_location = "東京都渋谷区"
    event_description = "プロジェクトの進捗会議"
    
    # ISOフォーマットの時間
    start_time = datetime.datetime(2024, 9, 20, 10, 0).isoformat()
    end_time = datetime.datetime(2024, 9, 20, 11, 0).isoformat()

    # カレンダーにイベントを追加
    add_event_to_calendar(creds, event_summary, start_time, end_time, event_location, event_description)