import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from google.oauth2.service_account import Credentials
import gspread
import time

background_image_path = r"C:\temp\SensorGraph\.SensorGraph\Scripts\image\オフィス間取り_什器配置用.png"

# グローバル変数としてセンサー調整値を定義
sensor_adjustments = {
    'A': 200,  
    'B': 120,  
    'C': 200
}

# 認証情報の設定
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

gc = None
sheet = None

def connect_to_google():
    global gc, sheet
    try:
        credentials = Credentials.from_service_account_file(
            r"C:\Users\kento\Downloads\distancesensoraltlog-40bfa413dfad.json",
            scopes=scopes
        )
        gc = gspread.authorize(credentials)
        
        # スプレッドシートのURL
        spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Uq4_YJZQwr3oJGnIwPRro1T3rezWOYiyBrEhOAgpYyg/edit?gid=0#gid=0"
        spreadsheet = gc.open_by_url(spreadsheet_url)
        sheet = spreadsheet.worksheet("RawData")
    except Exception as e:
        st.error(f"Google API 接続エラー: {e}")
        st.stop()

connect_to_google()

def get_data():
    """スプレッドシートのデータを取得し、DataFrameに変換"""
    global sensor_adjustments, sheet
    
    for _ in range(3):  # 最大3回リトライ
        try:
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Sensor_NumberがA, B, Cのデータのみ取得
            df = df[df['Sensor_Number'].isin(['A', 'B', 'C'])]
            
            # 最新のデータを取得（タイムスタンプでソート）
            df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])
            latest_df = df.sort_values(by='TimeStamp', ascending=False).drop_duplicates(subset=['Sensor_Number'])
            
            # Sensor_Numberごとに異なる値を減算
            if 'Sensor_RawData' in latest_df.columns:
                latest_df['Sensor_RawData'] = latest_df.apply(
                    lambda row: sensor_adjustments.get(row['Sensor_Number'], 0) - row['Sensor_RawData'], axis=1
                )
            else:
                latest_df['Sensor_RawData'] = 0  # データがない場合のデフォルト値
            
            return latest_df
        except Exception as e:
            st.warning(f"データ取得エラー: {e}。再試行します...")
            time.sleep(2)
            connect_to_google()
    
    st.error("データ取得に失敗しました。")
    return pd.DataFrame()

# Streamlit UI
st.title("Sensor Data Viewer")

# バブルチャート用の座標設定
coordinates = {
    'A': {'x': 6.2, 'y': 1.7},
    'B': {'x': 4.5, 'y': 4.4},
    'C': {'x': 7.2, 'y': 4.8}
}

# グラフ表示用のプレースホルダーを作成
data_placeholder = st.empty()
chart_placeholder = st.empty()

# 自動更新（手動で止めることもできる）
stop_flag = st.checkbox("更新を停止する")

while not stop_flag:
    df = get_data()
    
    if df.empty:
        time.sleep(2)
        continue
    
    # データの表示を更新
    data_placeholder.dataframe(df)
    
    df['x'] = df['Sensor_Number'].map(lambda s: coordinates[s]['x'])
    df['y'] = df['Sensor_Number'].map(lambda s: coordinates[s]['y'])

    # バブルチャートの描画
    fig, ax = plt.subplots()
    img = mpimg.imread(background_image_path)
    ax.imshow(img, aspect=1, extent=[0, 10, 0, 10], zorder=0, alpha=0.7)
    
    # バブルの描画（色を Sensor_RawData に応じて変更）
    sc = ax.scatter(df['x'], df['y'], s=df['Sensor_RawData'].astype(float) * 10, c=df['Sensor_RawData'].astype(float), cmap='bwr', alpha=0.5)

    # ラベル追加
    for i, row in df.iterrows():
        ax.text(row['x'], row['y'], row['Sensor_Number'], fontsize=7, ha='center', va='center')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_title("最新センサーデータのバブルチャート", fontname="MS Gothic")

    # グラフの更新
    chart_placeholder.pyplot(fig)
    
    # 1秒待機
    time.sleep(1)