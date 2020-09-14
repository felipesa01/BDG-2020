from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import pandas as pd
import math

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
            

def year_cover(collection, tile, anos, grafico = 'scatter'):
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
            df.plot(kind=grafico,x='data',y='nuvem', title = i, ax=axs[z]);
        else:
            df.plot(kind=grafico,x='data',y='nuvem', title = i);

            
def get_max(collection, tile, anos):
    dfs_max = [] 
    for i in anos:
        sql = "SELECT id, cover \
               FROM metadata_metrics \
               WHERE pathrow = '" + tile + "' \
               and cover = (SELECT max(cover) \
                            FROM metadata_metrics \
                            WHERE pathrow = '" + tile + "' \
                            and to_char(date_img, 'YYYY') = '" + i + "' \
                            and collection = '" + collection + "' \
                            );"     
        
        engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
        df = pd.read_sql_query(sql,con=engine)
        df.columns = ['id', "max_" + i]
        dfs_max.append(df)
    
    return dfs_max


def get_min(collection, tile, anos):
    dfs_min = [] 
    for i in anos:
        sql = "SELECT id, cover \
               FROM metadata_metrics \
               WHERE pathrow = '" + tile + "' \
               and cover = (SELECT min(cover) \
                            FROM metadata_metrics \
                            WHERE pathrow = '" + tile + "' \
                            and to_char(date_img, 'YYYY') = '" + i + "' \
                            and collection = '" + collection + "' \
                            );"     
        
        engine = create_engine('postgresql://postgres:postgres@localhost/bdc3')
        df = pd.read_sql_query(sql,con=engine)
        df.columns = ['id', "min_" + i]
        dfs_min.append(df)
    
    return dfs_min
        
        
        
        
        
        