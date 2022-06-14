'''
#-----------------------------------------------------------------------------#
                               FERRAMENTAS/FUNÇÕES                                            
#-----------------------------------------------------------------------------#
'''
import time
import sqlite3
import requests
import numpy as np
import pandas as pd
from datetime import datetime,timedelta
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from yahooquery import Ticker
import string
import plotly.graph_objects as go
import os
from utils.constants import dict_state

#modelo cruzamento de medias moveis
def model_mm(df):  
    papel = df.index.get_level_values(0).unique().item()
    media_curta, media_media, media_longa = 3, 7, 15
    cl_mm = ClassificadorTendenciaMM(media_curta=media_curta,
                                        media_longa=media_longa,
                                        media_media=media_media)
    valores = df['close']

    cl_mm.fit(valores)

    df['classificacoes'] = cl_mm.predict(valores)

    df.sort_index(ascending=False, level=0, inplace=True)
    estado = df['classificacoes'][0]

    map_estado_op = {
        'subindo': 'compra', 'baixando': 'venda', 'indeterminado': 'indeterminado'}

    report_value = {'PAPEL': papel, 'Estratégia': 'Cruzamento de medias', "Viabilidade Estratégica": 'Não', "Tipo de operação": map_estado_op[
        estado], "Stop": 'Sem stop', "Alvo": "Próximo cruzamento", "Parâmetros": f"Media curta:{media_curta}, \n Media media:{media_media}, \n Media longa:{media_longa}"}

    if estado != 'indeterminado':
        report_value['Viabilidade Estratégica'] = 'Sim'
    
    return report_value

#modelo compra e venda em oscilações com tendência de alta
def model_storm(df):
    # TRANSFORM STORM
    papel = df.index.get_level_values(0).unique().item()
    
    media_curta, media_media, media_longa, media_mlonga = 4, 9, 35, 80
    medias = {'curta': media_curta, 'media': media_media,
                'longa': media_longa, 'mlonga': media_mlonga}
    meds = medias_moveis(s=df['close'], medias=medias, nmed=4)

    # boleano com informação se todas as derivadas sao positivas
    bol_der_sub = duv_meds_subindo(meds)

    if bol_der_sub==True:
        # analise topos e fundos
        df_123 = umdoistres(df)
        ontem = df_123.iloc[0, :]
        anteontem = df_123.iloc[1, :]

        if anteontem['is_fundo']:    
            antesanteontem = df_123.iloc[2, :]
            stop = ontem['low']
            o_compra = ontem['high']+0.01

            # exapansao fibo
            e1 = 0.618
            e2 = 1.618
            cempcento = antesanteontem['high']-anteontem['low']

            # variacoes
            v1 = cempcento*e1
            v2 = cempcento*e2

            alvo_1 = v1 + ontem['low']
            alvo_2 = v2 + ontem['low']

            report_value = {'PAPEL': papel, 'Estratégia': 'Derivada + das 4 médias e 123', "Viabilidade Estratégica": 'Sim', "Tipo de operação": "Compra na tendência de alta", "Stop": round(stop,2),
                            "Alvo": f"1º Fibbo:{round(alvo_1,2)}, \n 2º Fibbo:{round(alvo_2,2)}", "Parâmetros": f"Media curta:{media_curta}, \n Media media:{media_media}, \n Media longa:{media_longa}, \n Media muito longa:{media_mlonga}"}
            return report_value
    elif bol_der_sub==False:
        report_value = {'PAPEL': papel, 'Estratégia': 'Derivada + das 4 médias e 123', "Viabilidade Estratégica": 'Não', "Tipo de operação": "", "Stop": '',
                        "Alvo": "", "Parâmetros": f"Media curta:{media_curta}, \n Media media:{media_media}, \n Media longa:{media_longa}, \n Media muito longa:{media_mlonga}"}
        return report_value

#extrai valores historicos da api
def get_papel_values(papel_alias):
   
    ticker = Ticker(papel_alias)
    
    sum = ticker.summary_detail
    if sum[papel_alias] !=  "No fundamentals data found for any of the summaryTypes=summaryDetail":    
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        ticker_hist = ticker.history(start=start, end=end)
        if isinstance(ticker_hist, pd.DataFrame):    
            ticker_hist.sort_values(by='date', ascending = False, inplace=True)
        else:
            pass
    else:
        ticker_hist = 0
        
    return ticker_hist

#Detecta topo e fundo
def umdoistres(df):

    dif_post_h = df['high'].diff(1).values    
    dif_ant_h = df['high'].diff(-1).values    
    dif_post_l = df['low'].diff(1).values    
    dif_ant_l = df['low'].diff(-1).values    

    #se ambas dif forem >0, é um topo
    is_topo = (dif_post_h>0) * (dif_ant_h>0) #* (dif_post_l>0) *(dif_ant_l>0)
    is_fundo = (dif_post_l<0) * (dif_ant_l<0) #* (dif_post_h<0) * (dif_ant_h<0) 

    df['is_fundo'] = is_fundo
    df['is_topo'] = is_topo

    return df

#Verifica se 4 medias moveis diferentes tem derivada positiva
def duv_meds_subindo(meds):
    bol_dmed_pos = [(med[0]-med[1])>0 for med in meds]
    return all(bol_dmed_pos)

#calcula medias moveis
def medias_moveis(s,medias = {'curta':4, 'media':9, 'longa':35, 'mlonga' : 80}, nmed = 3):
    media_movel_curta = s.rolling(window=medias['curta']).mean().shift(1-medias['curta'])
    media_movel_media = s.rolling(window=medias['media']).mean().shift(1-medias['media'])
    media_movel_longa = s.rolling(window=medias['longa']).mean().shift(1-medias['longa'])
    media_movel_mlonga = s.rolling(window=medias['mlonga']).mean().shift(1-medias['mlonga'])
    ls_mm = [media_movel_curta,media_movel_media, media_movel_longa, media_movel_mlonga]
    return ls_mm[:nmed]

#classifica medias móveis baseado na posição relativa entre as curvas
def classificar_estado_mm(s, s_curta, s_media, s_longa):

    """Função classifica acao baseada na tendencia representada pelas medias moveis
        input -
        s:uma série com os valores do ativo;
        curta:uma série com os valores da media móvel curta
        média:uma série com os valores da media móvel média
        longa:uma série com os valores da média móvel longa 

        output-
        é uma serie com a respectiva açao"""

    #criando booleanos para representar os cruzamentos
    I = s_media>s_curta
    II = s_media>s_longa
    III = s_longa>s_curta
    #

    #decodificando significado dos estados I, II e III. representa a posição das linhas 
    # médias móveis verticalmente de baixo para cima.
    dict_decode = {'FalseTrueFalse' :('curta', 'media', 'longa'),
            'FalseFalseFalse':('curta', 'longa', 'media'),
            'TrueTrueFalse'  :('media', 'curta', 'longa'),
            'TrueTrueTrue'   :('media', 'longa', 'curta'),
            'FalseFalseTrue' :('longa', 'curta', 'media'),
            'TrueFalseTrue'  :('longa', 'media', 'curta')}

    #indexando a combinação de estados 
    s_referencia  = I.map(str)+II.map(str)+III.map(str) #TODO só string, pode gerar direto comoo string

    #decodificando indexação booleana
    s_estado = s_referencia.map(dict_decode)

    #criando serie para representar o estado passado
    s_passado = s_estado.shift(-1)

    #serie que representa a sequencia de estados
    s_sequencia_estados = s_passado + s_estado

    return s_sequencia_estados

#Pela mudança de posição relativa das medias moveis, determina momento de entrada e saida.
def classifica_tendencia_mm(s_sequencia_estados):
            
    #decodificando significado da sequencia de estados em ações
    dict_comp_est = c.dict_state
    s_sequencia_estados = pd.Series(s_sequencia_estados)

    comportamento = s_sequencia_estados.map(dict_comp_est)

    comportamento.replace(np.nan, 'indeterminado', inplace = True)

    return comportamento.to_numpy()

#Classe do scikit para ficar mais arrumado, foi inutilizado, meio desnecessário.
class ClassificadorTendenciaMM(ClassifierMixin, BaseEstimator):
    """ Classifica a tendência entre alta, baixa e indeterminada.
    A classificação é baseada em médias móveis.
    Parameters
    ----------
    media_curta : int, default='10'
        Um parâmetro para o intervalo considerado na média curta.
    media_media : int, default='30'
        Um parâmetro para o intervalo considerado na média média.
    media_longa : int, default='80'
        Um parâmetro para o intervalo considerado na média longa.
    
    Attributes
    ----------
    X_ : ndarray, shape (n_samples, n_features)
        The input passed during :meth:`fit`.
    classes_ : ndarray, shape (n_classes,)
        The classes seen at :meth:`fit`.
    """
    def __init__(self, media_curta = 10, media_media =30 , media_longa = 80, media_mlonga =90):
        self.media_curta = media_curta
        self.media_media = media_media
        self.media_longa = media_longa
        self.media_mlonga = media_mlonga

    def fit(self, X, y=None):
        """A reference implementation of a fitting function for a classifier.
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The training input samples.
    
        Functions
        ----------
        medias_moveis: retorna medias moveis nos 3 intervalos escolhidos
        classificar_tendencia_MM: classifica a tendencia a partir do cruzamendo das MM

        Returns
        -------
        self : object
            Returns self.
        """

        # Store the classes seen during fit
        self.classes_ = np.array(['baixando', 'subindo', 'indeterminado'])
        
        s_curta, s_media, s_longa = medias_moveis(X,medias = {'curta':self.media_curta, 'media':self.media_media, 'longa':self.media_longa, 'mlonga' : self.media_mlonga})

        self.X_ =  classificar_estado_mm(X, s_curta, s_media, s_longa)

        

        # Return the classifier
        return self

    def predict(self, X, y=None):
        """ A reference implementation of a prediction for a classifier.
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The input samples.
        Returns
        -------
        y : ndarray, shape (n_samples,)
            The label for each sample is the label of the closest sample
            seen during fit.
        """

        
        
        return classifica_tendencia_mm(self.X_)

#Faz um gráfico bacana
def make_graph(df,papel):

    curta,media,longa = medias_moveis(df['close'],medias = {'curta':4, 'media':9, 'longa':35, 'mlonga' : 80})
    df['curta']=curta
    df['media']=media
    df['longa']=longa


    df = df.iloc[0:30].copy()

    df.reset_index(inplace = True)



    fig = go.Figure(data=[go.Candlestick(x=df['date'],
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'])])


    max(df['date'])
    x0 = max(df['date'])-timedelta(days=1)
    x1 = max(df['date'])
    y0 = df['close'][df['date']==x0].item()
    y1 = df['close'][df['date']==x1].item()

    fig.update_layout(
        title=f'Cotação {papel} B3 ',
        yaxis_title='R$'
    )

    fig.update_layout(xaxis_rangeslider_visible=False)

    fig.add_trace(go.Scatter(
        x=[x1],
        y=[y1],
        mode="markers",
        opacity=0.7,
        name="Reversão",
        textposition="middle center",
        marker=dict(
                color='LightSkyBlue',
                size=30,
                line=dict(
                    color='MediumPurple',
                    width=2
                )
            ),
            showlegend=False
    ))

    fig.add_scatter(x=df['date'], y=df['curta'], mode='lines',name = 'curta')
    fig.add_scatter(x=df['date'], y=df['media'], mode='lines',name = 'media')
    fig.add_scatter(x=df['date'], y=df['longa'], mode='lines',name = 'longa')
 
    return fig.to_image(format="png")

#Consulta banco para backtesting
def get_symbols(path_base = path_base):

    path_dados = 'Dados'
    path_files = os.path.join(path_base, path_dados)
    path_sqlite = os.path.join(path_files,'hist_b3.db')
    con = sqlite3.connect(path_sqlite)
    df = pd.read_sql(con = con, sql = "SELECT * FROM symbols_y")
    return df['yahoo_symbols'].to_list()
