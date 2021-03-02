
import itertools
import plotly.express as px
import pandas as pd

"""
Esse script foi para testar algumas combinações de variação de posição relativa entre as medias móveis, pode ignorar
"""

mm_values = [80,35,9,4]
mm_names = ['mlonga', 'longa', 'media', 'curta']
dict_mm_nv = {k:v for k,v in zip(mm_names,mm_values)}
dict_mm_vn = {v:k for k,v in zip(mm_names,mm_values)}

mm = mm_values
#todas as posições que as linhas podem ter
ls_per = list(itertools.permutations(mm, len(mm_values)))

#mudanças de estado
mudancas_estado = list(itertools.permutations(ls_per, 2))


#TESE PRED
import sqlite3
import pandas as pd
from utils_mm import ClassificadorTendenciaMM, medias_moveis, make_graph, get_symbols

con = sqlite3.connect(r'/home/fm/Documents/swing_bbot3/Dados/hist_b3.db')

home = pd.read_sql(con=con, sql= 'SELECT * FROM COT_B3')
sub = home[home.COD_NEG==home['COD_NEG'].unique()[2]]
data = sub['P_MEDIO']

cl_mm = ClassificadorTendenciaMM()

cl_mm.fit(data)


def classifica_tendencia_mm(s_sequencia_estados):
            
    #decodificando significado da sequencia de estados em ações
    dict_comp_est = {('curta', 'media', 'longa','curta', 'media', 'longa'): 'indeterminado',
                    ('curta', 'media', 'longa', 'curta', 'longa', 'media'): 'indeterminado',
                    ('curta', 'media', 'longa', 'media', 'curta', 'longa'): 'indeterminado',
                    ('curta', 'media', 'longa', 'media', 'longa', 'curta'): 'indeterminado',
                    ('curta', 'media', 'longa', 'longa', 'curta', 'media'): 'indeterminado',
                    ('curta', 'media', 'longa', 'longa', 'media', 'curta'): 'indeterminado',
                    ('curta', 'longa', 'media', 'curta', 'media', 'longa'): 'baixando',
                    ('curta', 'longa', 'media', 'curta', 'longa', 'media'): 'indeterminado',
                    ('curta', 'longa', 'media', 'media', 'curta', 'longa'): 'indeterminado',
                    ('curta', 'longa', 'media', 'media', 'longa', 'curta'): 'indeterminado',
                    ('curta', 'longa', 'media', 'longa', 'curta', 'media'): 'subindo',
                    ('curta', 'longa', 'media', 'longa', 'media', 'curta'): 'indeterminado',
                    ('media', 'curta', 'longa', 'curta', 'media', 'longa'): 'baixando',
                    ('media', 'curta', 'longa', 'curta', 'longa', 'media'): 'indeterminado',
                    ('media', 'curta', 'longa', 'media', 'curta', 'longa'): 'indeterminado',
                    ('media', 'curta', 'longa', 'media', 'longa', 'curta'): 'indeterminado',
                    ('media', 'curta', 'longa', 'longa', 'curta', 'media'): 'indeterminado',
                    ('media', 'curta', 'longa', 'longa', 'media', 'curta'): 'indeterminado',
                    ('media', 'longa', 'curta', 'curta', 'media', 'longa'): 'indeterminado',
                    ('media', 'longa', 'curta', 'curta', 'longa', 'media'): 'indeterminado',
                    ('media', 'longa', 'curta', 'media', 'curta', 'longa'): 'baixando',
                    ('media', 'longa', 'curta', 'media', 'longa', 'curta'): 'indeterminado',
                    ('media', 'longa', 'curta', 'longa', 'curta', 'media'): 'indeterminado',
                    ('media', 'longa', 'curta', 'longa', 'media', 'curta'): 'subindo',
                    ('longa', 'curta', 'media', 'curta', 'media', 'longa'): 'indeterminado',
                    ('longa', 'curta', 'media', 'curta', 'longa', 'media'): 'indeterminado',
                    ('longa', 'curta', 'media', 'media', 'curta', 'longa'): 'indeterminado',
                    ('longa', 'curta', 'media', 'media', 'longa', 'curta'): 'indeterminado',
                    ('longa', 'curta', 'media', 'longa', 'curta', 'media'): 'indeterminado',
                    ('longa', 'curta', 'media', 'longa', 'media', 'curta'): 'subindo',
                    ('longa', 'media', 'curta', 'curta', 'media', 'longa'): 'indeterminado',
                    ('longa', 'media', 'curta', 'curta', 'longa', 'media'): 'indeterminado',
                    ('longa', 'media', 'curta', 'media', 'curta', 'longa'): 'indeterminado',
                    ('longa', 'media', 'curta', 'media', 'longa', 'curta'): 'indeterminado',
                    ('longa', 'media', 'curta', 'longa', 'curta', 'media'): 'baixando',
                    ('longa', 'media', 'curta', 'longa', 'media', 'curta'): 'indeterminado'}

    s_sequencia_estados = pd.Series(s_sequencia_estados)

    comportamento = s_sequencia_estados.map(dict_comp_est)
    return comportamento

classifica_tendencia_mm(cl_mm.X_).value_counts()

pd.Series(cl_mm.predict(cl_mm.X_)).value_counts()





