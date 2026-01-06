import requests
from datetime import datetime, timedelta


# 假設在 Airflow DAG 中執行
def fetch_yesterdays_10min_data():
    CWA_HISTORY_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/history/O-A0002-001"  # 以十分鐘雨量為例
    API_KEY = "您的授權碼"

    # 1. 計算昨天的日期
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    # 2. 遍歷一整天的每十分鐘
    for hour in range(24):
        for minute in range(0, 60, 10):
            # 3. 組合目標時間字串 (格式需參考API文件)
            target_time_str = f"{yesterday_str}T{hour:02d}:{minute:02d}:00"

            print(f"正在嘗試取得 {target_time_str} 的資料...")

            params = {"Authorization": API_KEY, "time": target_time_str}

            # 4. 呼叫 History API
            response = requests.get(CWA_HISTORY_API_URL, params=params)

            if response.status_code == 200:
                # 這裡的邏輯是假設 API 會回傳下載連結
                # 您需要根據實際的 API 回應來解析並下載檔案
                file_download_url = response.json().get(
                    "download_url"
                )  # 假設的回應格式

                if file_download_url:
                    # download_and_process_file(file_download_url)
                    print(f"成功取得下載連結: {file_download_url}")
                else:
                    print(f"在 {target_time_str} 找不到資料檔案。")
            else:
                print(f"請求失敗，狀態碼: {response.status_code}")


# 實際使用時，您需要詳細閱讀 History API 的文件來確定請求和回應的確切格式。
