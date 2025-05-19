import requests
import pandas as pd
from dotenv import load_dotenv
import os
import io

load_dotenv()

API_KEY = os.getenv('API_KEY')

BASE_URL = "http://api.e-stat.go.jp/rest/3.0/app/getSimpleStatsData"

params = {
    "appId": API_KEY,
    "lang": "J",
    "metaGetFlg": "Y",
    "cntGetFlg": "N",
    "explanationGetFlg": "Y",
    "annotationGetFlg": "Y",
    "sectionHeaderFlg": "1",
    "replaceSpChars": "0",
}

stats_data_ids = ["0004008041", "0003448229", "0003459019"]

for stats_data_id in stats_data_ids:
    params["statsDataId"] = stats_data_id
    
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        print(f"\nstatsDataId: {stats_data_id}")
        print(f"")
        print("Return 100 characters of API response:")
        print(response.text[:100])  
        
        csv_data = io.StringIO(response.text)
        
        try:
            df = pd.read_csv(csv_data, sep=',')  
        except:
            csv_data.seek(0) 
            try:
                df = pd.read_csv(csv_data, sep='\t')
            except:
                print("Can't parse CSV data, please check the original data format")
                continue
        
        if df.empty:
            print("The dataframe is empty. Please check the original data format")
        else:
            if not os.path.exists('raw'):
                os.makedirs('raw')
            
            output_file = os.path.join('raw', f'japan_population_raw_{stats_data_id}.csv')
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"Save as: {output_file}")
        
        print("\n First 5 rows:")
        print(df.head(5))  
    else:
        print(f"Request failed, status code: {response.status_code}")
        print(response.text)