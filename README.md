# b3bot
 Bot com dados da B3 que envia resultados para email. Analise técnica bem simples, aberto a dúvidas e comits
Estratégias usadas: Cruzamento de médias móveis e compra em topo com venda em vale (stop loss e stop gain por fibonacci)
O script gera decisão de compra e venda antes da abertura de mercado com dados diários e envia pro email via airflow. 

#main.py
app.py-> Workflow que faz a consulta dos valores da B3, realiza a analise, armazena resultados gera excel formatado para envio por email

#utilitarios
gera_banco.py -> Script que gera um banco sqlite com dados históricos
utils_mm.py -> Armazena funções
dag_airflow.py-> Script para configurar a dag no airflow


Qualquer dúvida podem mandar mensagem, nenhuma path está configurada de forma geral. Para rodar no seu pc precisa de configurações.
