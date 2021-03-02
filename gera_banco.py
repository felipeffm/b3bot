import pandas as pd
import os
import sqlite3


"""Esse script é um parser da series historica fornecida para b3. O resultado é salvo em um banco sqlite"""

#path
path_base = '/home/fm/Documents/swing_bbot3'
path_dados = 'Dados'
path_files = os.path.join(path_base, path_dados)
files_bov = os.listdir(path_files)
files_bov_ =[os.path.join(path_files, filepath)  for filepath in files_bov if filepath.endswith('.TXT')]

path_sqlite = os.path.join(path_files,'hist_b3.db')
con = sqlite3.connect(path_sqlite)

#functions
def decoder_b3format(x):
    """Faz o decode do formato fornecido pela B3 em http://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/historico/mercado-a-vista/series-historicas/

    Args:
        x [str]: string que representa a informação de linha passada pela b3

    Returns:
        [type]: [description]
    """
    return {'DATA_PREGAO':x[2:10],
            'COD_NEG':x[12:24],
            'MOEDA_REF':x[52:56],
            'P_ABERTURA':x[56:69],
            'P_MAX':x[69:82],
            'P_MIN':x[82:95],
            'P_FECHAMENTO':x[108:121],
            'P_MEDIO':x[95:108],
            'VOLUME_TITULOS':x[170:188],
            'NEGOCIACOES_PAPEL':x[147:152],
            'TP_MERC':x[24:27]}

def format_b3_txt(path_txt):
    """Aplica o decoder em todas as linhas, formata e retorna df

    Args:
        path_txt [str]: path do arquivo txt enviado pela bovespa

    Returns:
        [dataframe]
    """
    nome_arq = path_txt.split('/')[-1]
    df = pd.read_csv(path_txt)

    geracao_arquivo = df.columns[0].split(' ')[1]

    ls_values = df.values.tolist()[:-1]
    flat_list = [item for sublist in ls_values for item in sublist]
    ls_dict_df = list(map(decoder_b3format,flat_list))
    df_ = pd.DataFrame(ls_dict_df)

    df_['DATA_PREGAO'] = pd.to_datetime(df_['DATA_PREGAO'])
    df_['COD_NEG'] = df_['COD_NEG'].str.strip()
    df_['MOEDA_REF'] = df_['MOEDA_REF'].str.strip()
    df_[['P_ABERTURA', 'P_MAX', 'P_MIN','P_FECHAMENTO', 'P_MEDIO']] = df_[['P_ABERTURA', 'P_MAX', 'P_MIN','P_FECHAMENTO', 'P_MEDIO']].astype(float)*0.01
    df_[['VOLUME_TITULOS', 'NEGOCIACOES_PAPEL', 'TP_MERC']] = df_[['VOLUME_TITULOS', 'NEGOCIACOES_PAPEL','TP_MERC']].astype(int)
    df_['NOME_ARQUIVO_B3'] = nome_arq
    df_['DT_GERACAO_ARQ'] = geracao_arquivo
    df_['DT_GERACAO_ARQ'] = pd.to_datetime(df_['DT_GERACAO_ARQ'])
    return df_

def filtro_merc_vista(df):
    return df[df['TP_MERC'] == 10]

ls_df = list(map(format_b3_txt,files_bov_))

ls_df = list(map(filtro_merc_vista,ls_df))

full_df = pd.concat(ls_df)

full_df.to_sql(con = con, name = 'cot_b3', if_exists='replace')

#FILTREI ESSA TABELA, NOMES DE TITULO TINHAM ENTRADO
df_yahoo = pd.read_csv(os.path.join(path_files,'yahoosymbols.csv'))
df_yahoo.to_sql(con = con, name = 'symbols_yahoo', if_exists='replace')