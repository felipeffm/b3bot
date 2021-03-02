from utils_mm import get_symbols, get_papel_values, model_mm, model_storm
import numpy as np
#import telegram
from tqdm import tqdm
import pandas as pd
import time
from datetime import datetime



# EXTRACT
papeis = get_symbols()

dados_analise = []
resp_hist = []



# TRANSFORM
for papel in tqdm(papeis):
    try:
        df = get_papel_values(papel)
        
        resp_hist.append(df)

        if isinstance(df, pd.DataFrame):

            if len(df) > 30:

                dados_analise.append(model_mm(df))
                dados_analise.append(model_storm(df))

            else:
                print(f'Papel sem dados {papel}')
    except KeyError:
        pass


# TREAT
dados_analise = [
    dicionario for dicionario in dados_analise if dicionario is not None]
df_analise = pd.DataFrame.from_dict(dados_analise)

df_analise['DATA PROCESSAMENTO'] = datetime.now().strftime('%m/%d/%Y')
papeis_analisados = ','.join(df_analise.PAPEL.unique())
df_load = df_analise[df_analise['Viabilidade Estratégica'] == 'Sim'].copy()
df_load = df_load[['PAPEL', 'Alvo', 'Stop', 'Viabilidade Estratégica', 'Estratégia', 'Tipo de operação',
                   'Parâmetros', 'DATA PROCESSAMENTO']].copy()

df_load.to_pickle(f"analise_{datetime.now().strftime('%m.%d.%Y')}.pck")

# LOAD == Envia email com resultado e armazena local
if df_load.shape[0]>0:
    # configuracao planilha
    excel_file_path = f"/home/fm/Documents/swing_bbot3/Dados/analise_{datetime.now().strftime('%m.%d.%Y')}.xlsx"
    writer = pd.ExcelWriter(excel_file_path, engine='xlsxwriter')
    df_load.to_excel(writer, sheet_name='Papeis', index=False, freeze_panes=(0, 8))
    workbook = writer.book
    for column in df_load:
        column_length = max(df_load[column].astype(
            str).map(len).max(), len(column))
        col_idx = df_load.columns.get_loc(column)
        writer.sheets['Papeis'].set_column(col_idx, col_idx, column_length)
    writer.save()

    # salvando cache
    historico = pd.concat([pd.DataFrame(response)
                        for response in resp_hist if len(response.keys()) > 2])
    historico.to_pickle(f"historico_{datetime.now().strftime('%m.%d.%Y')}.pck")
