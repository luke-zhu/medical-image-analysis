from datetime import datetime

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'luke',
    'start_date': datetime(2018, 6, 26),
}

dag = DAG(dag_id='dropbox_to_gcs', default_args=default_args)

op = BashOperator(task_id='dropbox_to_gcs_op',
                  bash_command='python3 /home/lukezhu/elvo-analysis/etl/dropbox_to_gcs.py',
                  dag=dag)
