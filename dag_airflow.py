from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.dates import days_ago
import airflow


"""dag do airflow usada para enviar um email com resultados"""

default_args = {
    'owner': 'airflow',
    'email': ['felipefm@id.uff.br'], #coloque seu email aqui
    'email_on_failure': False,
    'email_on_retry': False,
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)}


dag = DAG(dag_id='b3_info',
          default_args=default_args,
          schedule_interval='0 8 * * 1-5',
          #dagrun_timeout=timedelta(minutes=5),
          start_date=datetime(2019, 1, 1) ,
          tags=['acoes','swing','b3']
          )

tsk_B3 = BashOperator(
    task_id='analisa_papeis',
    bash_command='cd /home/fm/Documents/swing_bbot3/Scripts && /home/fm/miniconda3/envs/b3/bin/python /home/fm/Documents/swing_bbot3/Scripts/app.py',
    dag=dag,
    depends_on_past=False
)


mail_results = EmailOperator(
        task_id='send_result',
        to=['felipefm@id.uff.br'],
        subject='Análise Gráfica Diária',
        html_content=""" <h3>Bom dia, humano. Seguem resultados anexos.</h3> """,
        files = [f"/home/fm/Documents/swing_bbot3/Dados/analise_{datetime.now().strftime('%m.%d.%Y')}.xlsx"],
        dag=dag
)

check_results_storage = FileSensor(
    
    task_id='sense_result',
    filepath = f"/home/fm/Documents/swing_bbot3/Dados/analise_{datetime.now().strftime('%m.%d.%Y')}.xlsx",
    poke_interval=3,
    dag=dag
)

tsk_B3 >> check_results_storage >> mail_results
