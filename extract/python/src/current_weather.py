import sys
from dotenv import load_dotenv
load_dotenv()
import requests
import os
import json
import datetime

def main(argv):
    # TEMPファイル出力先
    TEMP_FILE_DIR = os.environ.get("TEMP_FILE_DIR")

    # APIキー
    API_KEY = os.environ.get("OWM_API_KEY")
    print(API_KEY)

    # 対象とする都道府県
    pref_dict = {
        "東京都":{
            "id":"1850144"
        },
        "神奈川県":{
            "id":"1860291"
        },
    }

    # 気候情報のJSONリスト
    weather_json_list = []

    # 都市ごとの気候を取得する
    for pref in pref_dict.values():

        # リクエスト
        response = requests.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "id": pref["id"],
                    "appid": API_KEY,
                    "units": "metric",
                    "lang": "ja",
                },
            )
        weather_json_list.append(response.text)
    
    # JSONL形式で出力する
    today = datetime.datetime.today().strftime("%Y%m%d")
    filename = f"weather_{today}.jsonl"
    with open(os.path.join(TEMP_FILE_DIR,filename),mode="w",encoding="utf-8") as f:
        for json_text in weather_json_list:
            f.write(json_text)
            f.write("\n")

if __name__ == '__main__':
    sys.exit(main(sys.argv))