from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import pandas as pd
import math
from datetime import datetime
from datetime import timedelta
import matplotlib.dates as mdates
import numpy as np

#
# Otimizar!!! 
# - Retorno das funções
# - Criar função plot
#

def get_data_mean(collection, tile, anos, lim_min = None, lim_max = None):
    if lim_min == None:
        sql_min = ''
    else:
        sql_min = "and cover >= " + str(lim_min)
        
    if lim_max == None:
        sql_max = ''
    else:
        sql_max = "and cover <= " + str(lim_max)
    
    mes = [['{:02}'.format(i)] for i in np.arange(1,13)]
    df_final = pd.DataFrame(mes, columns=['mes'])
    
    for i in anos:
        sql = "SELECT to_char(date_img, 'MM') as mes, avg(cover) as {ano} \
              FROM metadata_metrics \
              WHERE to_char(date_img, 'YYYY') = '".format(ano='"{}"'.format(i)) + i + "' \
              and pathrow = '" + tile + "' \
              and collection = '" + collection + "'" + sql_min + sql_max + " \
              GROUP BY to_char(date_img, 'MM');"
        
        engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
        df = pd.read_sql_query(sql,con=engine)
               
        df_final = df_final.merge(df, 'left', 'mes')
    
    df_final['mean'] = df_final.mean(axis=1, skipna=True, numeric_only=True)
    df_final['n_img'] = df_final.notna().sum(axis=1)-2
    df_final['mes'] = pd.to_datetime(df_final['mes'], format='%m')
    df_final.insert(1, 'mes_ext', df_final['mes'].map(lambda x: x.strftime("%b")))
    df_final['mes'] = pd.to_datetime(df_final['mes'], format='%m').dt.month  
       
    return df_final

def get_data_cover(collection, tile, anos, lim_min = None, lim_max = None):
    if lim_min == None:
        sql_min = ''
    else:
        sql_min = "and cover >= " + str(lim_min)
        
    if lim_max == None:
        sql_max = ''
    else:
        sql_max = "and cover <= " + str(lim_max)
    

    df_final = pd.DataFrame(columns=['id'])
    
    for i in anos:
        sql = """SELECT date_img as data, cover as "\
              """ + i + """\
              " FROM metadata_metrics \
              WHERE to_char(date_img, 'YYYY') = '""" + i + "' \
              and pathrow = '" + tile + "' \
              and collection = '" + collection + "'" + sql_min + sql_max
        
        engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
        df = pd.read_sql_query(sql,con=engine)
        df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
               
        df_final = pd.concat([df_final,df], ignore_index=True)
    
    
    df_final.drop(labels='id', axis=1, inplace=True)
    
    return df_final

def plot_mean(collection, tile, anos, lim_min = None, lim_max = None, ag=False, mean='', series=False):
    df = get_data_mean(collection, tile, anos, lim_min, lim_max)
    
    if series:
        plot = {}
        for ano in anos:
            for i in range(len(df)):
                key = datetime.strptime(str(df['mes_ext'][i]) + '-' + ano, '%b-%Y')
                key = key.replace(day=15)
                plot[key] = df[ano][i]

        lists = sorted(plot.items())
        x, y = zip(*lists)  

        years = mdates.YearLocator()   # every year
        months = mdates.MonthLocator(bymonth=(4,7,10))  # every month
        years_fmt = mdates.DateFormatter('%Y')
        month_fmt = mdates.DateFormatter('%b')


        fig, ax = plt.subplots(figsize=( 15, 5 ))

        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_fmt)
        ax.xaxis.set_minor_locator(months)
        ax.xaxis.set_minor_formatter(month_fmt)

        delta = timedelta(weeks=9)
        datemin = x[0] - delta
        datemax = x[-1] + delta
        ax.set_xlim(datemin, datemax)
        ax.set_ylim(0,100)

        ax.tick_params(which='major', length=7, pad=10, labelsize='large')
        ax.tick_params(which='minor', length=5, pad=5, labelcolor='grey')
        ax.grid(color='black', axis='x', linestyle='--', linewidth=.5, alpha=.5)
        ax.grid(color='grey', axis='x', linestyle='--', linewidth=.3, alpha=.6, which='minor')

        ax.set_ylabel("Cloud Cover Average (%)",labelpad=10, fontsize=12, fontweight='bold')
        ax.set_xlabel("Time",labelpad=10, fontsize=12, fontweight='bold')

#         ax.set_title()

        ax.plot(x, y) 
    
    else:
        if not ag:
            if len(anos) == 1:
                figsize = (15,4)

            else:
                figsize = (15,10)

            fig, ax = plt.subplots(len(anos), figsize=figsize, sharex=True)
            fig.subplots_adjust(wspace = .6)

            if len(anos) == 1:
                ax = np.array(ax)

            for ax, ano in zip(ax.flat,anos):
                ax.plot(df['mes_ext'], df[ano])
                ax.set_ylim(0,100)

                if len(anos) > 1:
                    ax.set_title(ano)

                ax.grid(color='grey', axis='x', linestyle='--', linewidth=.3, alpha=.8)

        else:
            fig, ax = plt.subplots(figsize=(15,4))

            alpha = 1
            for ano in anos:           
                if mean == 'all' and len(anos) > 1:
                    if ano == anos[0]:
                        alpha = .75
                        ax.plot(df['mes_ext'], df['mean'], label='Mean', color='black', linestyle='dashed', linewidth=2)
                        ax.set_ylim(0,100)

                elif mean == 'only' and len(anos) > 1:
                    ax.plot(df['mes_ext'], df['mean'], 
                            label='Mean {}'.format(tuple([int(i) for i in anos])),
                            color='black', 
                            linestyle='dashed', 
                            linewidth=2, 
                            marker='o')
                    
                    ax.set_ylim(0,100)

                    n = list(df['n_img'])
                    for i, txt in enumerate(n):
                        if df['mean'][i] >= 50:
                            y_label = df['mean'][i] - 12
                        else:
                            y_label = df['mean'][i] + 10

                        ax.annotate('n = ' + str(txt), (df['mes_ext'][i], y_label), ha='center')

                    break

                ax.plot(df['mes_ext'], df[ano], label=ano, alpha=alpha)
                ax.set_ylim(0,100)     

            ax.grid(color='grey', axis='x', linestyle='--', linewidth=.3, alpha=.8)
            ax.legend()

    #     fig.suptitle("Título genérico para agregado ou nao e um ou mais gráficos", y=0.95, fontsize=16)
        fig.add_subplot(111, frame_on=False)
        plt.tick_params(labelcolor="none", bottom=False, left=False)
        plt.ylabel("Cloud Cover Average (%)",labelpad=10, fontsize=12, fontweight='bold')
        plt.xlabel("Month",labelpad=10, fontsize=12, fontweight='bold')


def month_mean(collection, tile, anos, ag = False):
    
    if not ag:      
        if len(anos) > 1:
            fig, ax = plt.subplots(len(anos), 1)

            fig.subplots_adjust(hspace = .5, wspace=.1)

            for z,i in zip(range(len(anos)), anos):

                sql = "SELECT to_char(date_img, 'MM') as mes, avg(cover) as media \
                    FROM metadata_metrics \
                    WHERE to_char(date_img, 'YYYY') = '" + i + "' \
                    and pathrow = '" + tile + "' \
                    and collection = '" + collection + "' \
                    GROUP BY to_char(date_img, 'MM');"

                engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
                df = pd.read_sql_query(sql,con=engine)

                df.plot(kind='line',x='mes',y='media', ax=ax[z], title = i, figsize=(15, 10), legend=False, xlim=(-1,12), ylim=(0,100));
        
        else:
            sql = "SELECT to_char(date_img, 'MM') as mes, avg(cover) as media \
                FROM metadata_metrics \
                WHERE to_char(date_img, 'YYYY') = '" + anos[0] + "' \
                and pathrow = '" + tile + "' \
                and collection = '" + collection + "' \
                GROUP BY to_char(date_img, 'MM');"

            engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
            df = pd.read_sql_query(sql,con=engine)

            df.plot(kind='line',x='mes',y='media', title = anos[0], figsize=(15, 4), legend=False, xlim=(-1,12));
            
    else:
        fig, ax = plt.subplots(1, 1)

        for z,i in zip(range(len(anos)), anos):

            sql = "SELECT to_char(date_img, 'MM') as mes, avg(cover) as media \
                FROM metadata_metrics \
                WHERE to_char(date_img, 'YYYY') = '" + i + "' \
                and pathrow = '" + tile + "' \
                and collection = '" + collection + "' \
                GROUP BY to_char(date_img, 'MM');"

            engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
            df = pd.read_sql_query(sql,con=engine)
            df.columns = ['mes', i]

            df.plot(kind='line',x=0,y=1, ax=ax, title = 'Média mensal (Orbita/ponto:' + tile + ")", figsize=(15, 4), xlim=(-1,12));
            

def year_cover(collection, tile, anos, limiar = None, grafico = 'scatter'):
    row = math.ceil(len(anos)/2)
    if len(anos) > 1:
        fig, ax = plt.subplots(row, 2, figsize=(15, 10))
        fig.subplots_adjust(hspace = .3, wspace=.15)
        axs = ax.ravel()
        

    for z,i in zip(range(row*2), anos):

        sql = "SELECT date_img as data, cover as nuvem \
            FROM metadata_metrics \
            WHERE to_char(date_img, 'YYYY') = '" + i + "' \
            and collection = '" + collection + "' \
            and pathrow = '" + tile + "';"

        engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
        df = pd.read_sql_query(sql,con=engine)
        
        if len(anos) > 1:
            df.plot(kind=grafico,x='data',y='nuvem', title = i, ax=axs[z])
            if limiar:
                axs[z].hlines(limiar, min(df['data']), max(df['data']), color='r', lw= 0.5);
        else:
            df.plot(kind=grafico,x='data',y='nuvem', title = i)
            if limiar:
                axs[z].hlines(limiar, min(df['data']), max(df['data']), color='r', lw= 0.5);

            
def get_max(collection, tile, anos):
    dfs_max = {} 
    for i in anos:
        sql = "SELECT id, date_img, cover \
               FROM metadata_metrics \
               WHERE pathrow = '" + tile + "' \
               and to_char(date_img, 'YYYY') = '" + i + "' \
               and cover = (SELECT max(cover) \
                            FROM metadata_metrics \
                            WHERE pathrow = '" + tile + "' \
                            and to_char(date_img, 'YYYY') = '" + i + "' \
                            and collection = '" + collection + "' \
                            );"     
        
        engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
        df = pd.read_sql_query(sql,con=engine)
        df.columns = ['id','data','max']
        dfs_max[i] = df
    
    return dfs_max


def get_min(collection, tile, anos, zero=True):
    if zero:
        min_zero = ''
    else:
        min_zero = 'and cover > 0'
        
    dfs_min = {}
    for i in anos:
        sql = "SELECT id, date_img, cover \
               FROM metadata_metrics \
               WHERE pathrow = '" + tile + "' \
               and to_char(date_img, 'YYYY') = '" + i + "' \
               and cover = (SELECT min(cover) \
                            FROM metadata_metrics \
                            WHERE pathrow = '" + tile + "' \
                            and to_char(date_img, 'YYYY') = '" + i + "' \
                            and collection = '" + collection + "'" \
                            + min_zero + ");"     
        
        engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
        df = pd.read_sql_query(sql,con=engine)
        df.columns = ['id','data','min']
        dfs_min[i] = df
    
    return dfs_min
        
        
        
        
        
        