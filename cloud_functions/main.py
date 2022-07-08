import os
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import requests

import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
import logging

IAM_SCOPE = 'https://www.googleapis.com/auth/iam'
OAUTH_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
# If you are using the stable API, set this value to False
# For more info about Airflow APIs see https://cloud.google.com/composer/docs/access-airflow-api
USE_EXPERIMENTAL_API = False

AIRFLOW_CLIENT_ID = os.environ.get("AIRFLOW_CLIENT_ID")
WEB_SERVER_ID = os.environ.get("WEB_SERVER_ID") # {WEB_SERVER_ID}.appspot.com
DAG_NAME = "airflow_training"
FILE_PREFIX = "weather_"
FILE_SUFIX = ".json"

client = google.cloud.logging.Client()
client.setup_logging()

def trigger_dag(data,context=None):
    logging.debug("data:{data}")

    # ====== ファイル名のチェック ======
    file_name = data['name']
    logging.debug("file_name:{file_name}")
    
    yyyymmdd = file_name.replace(FILE_PREFIX,"").replace(FILE_SUFIX,"")
    logging.debug("yyyymmdd:{yyyymmdd}")

    # 数字ではない or 文字数が6ではない場合は処理を終了する
    if (not yyyymmdd.isdigit()) | (not len(yyyymmdd) == 6):
        return None
    
    # ====== Airflow REST API実行 ======

    if USE_EXPERIMENTAL_API:
        endpoint = f'api/experimental/dags/{DAG_NAME}/dag_runs'
        json_data = {'conf': data, 'replace_microseconds': 'false'}
    else:
        endpoint = f'api/v1/dags/{DAG_NAME}/dagRuns'
        json_data = {'conf': data}
    webserver_url = (
        'https://'
        + WEB_SERVER_ID
        + '.appspot.com/'
        + endpoint
    )

    logging.debug("webserver_url:{webserver_url}")

    # Make a POST request to IAP which then Triggers the DAG
    make_iap_request(
        webserver_url, AIRFLOW_CLIENT_ID, method='POST', json=json_data)

    # This code is copied from
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/main/iap/make_iap_request.py
# START COPIED IAP CODE
def make_iap_request(url, client_id, method='GET', **kwargs):
    """Makes a request to an application protected by Identity-Aware Proxy.
    Args:
      url: The Identity-Aware Proxy-protected URL to fetch.
      client_id: The client ID used by Identity-Aware Proxy.
      method: The request method to use
              ('GET', 'OPTIONS', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE')
      **kwargs: Any of the parameters defined for the request function:
                https://github.com/requests/requests/blob/master/requests/api.py
                If no timeout is provided, it is set to 90 by default.
    Returns:
      The page body, or raises an exception if the page couldn't be retrieved.
    """
    # Set the default timeout, if missing
    if 'timeout' not in kwargs:
        kwargs['timeout'] = 90

    # Obtain an OpenID Connect (OIDC) token from metadata server or using service
    # account.
    google_open_id_connect_token = id_token.fetch_id_token(Request(), client_id)

    # Fetch the Identity-Aware Proxy-protected URL, including an
    # Authorization header containing "Bearer " followed by a
    # Google-issued OpenID Connect token for the service account.
    resp = requests.request(
        method, url,
        headers={'Authorization': 'Bearer {}'.format(
            google_open_id_connect_token)}, **kwargs)
    if resp.status_code == 403:
        raise Exception('Service account does not have permission to '
                        'access the IAP-protected application.')
    elif resp.status_code != 200:
        raise Exception(
            'Bad response from application: {!r} / {!r} / {!r}'.format(
                resp.status_code, resp.headers, resp.text))
    else:
        return resp.text
# END COPIED IAP CODE