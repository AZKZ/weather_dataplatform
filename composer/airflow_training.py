import datetime
import airflow
from airflow.providers.google.cloud.operators.datafusion import CloudDataFusionStartPipelineOperator

import pendulum

# DAG内のオペレータ共通のパラメータを定義する。
default_args = {
    'owner': 'dataplatform-training',
    'depends_on_past': False,
    'email': [''],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
    # DAG作成日の午前2時(JST)を開始日時とする。
    'start_date': pendulum.today('Asia/Tokyo').add(hours=2)
}

# DAGを定義する。
with airflow.DAG(
    'airflow_training',
    default_args=default_args,
    catchup=False,
    schedule_interval=None,
    ) as dag:

    # Data Fusionのパイプラインを実行する。
    start_data_fusion_pipeline = CloudDataFusionStartPipelineOperator(
        location="us-west1",
        pipeline_name="pipline-training_v4",
        instance_name="pipeline-training",
        task_id="start_data_fusion_pipeline",
        runtime_args={ "name":"{{ dag_run.conf['name'] }}"}
    )

    # 各タスクの依存関係を定義する。
    start_data_fusion_pipeline