from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
import json
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, create_engine,select, SQLModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import plotly as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO


app = FastAPI()
#Debe tenerse en cuenta que hay acciones que pueden acelerar el proceso de llamada
#Crear consultas previas ahorra tiempo de ejecución
df = pd.read_excel('web_tables.xlsx')

#Vamos a crear una gráfica
frec_abs = df['Consejo_Popular'].value_counts(dropna=False)
frec_rel = df['Consejo_Popular'].value_counts(normalize=True)*100

#Gráfico de frecuencias
fre_gr= pd.DataFrame({'Frec_rel':frec_rel.round(2)})


#Esto es un apartado para la BBDD que quisiera incluir en el futuro
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite corre en 5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#definir connection

@app.get("/")
def root():
    return {
        "message": "Hi, this is my app!"
    }

#Crear una consulta condicionada por argumentos administrados a la api
#Con esto tengo una consulta que debe incorporar un parámetro,
#debo indicar en el parámetro que es de tipo Query(...), que como tal
#es obligatorio y viene de la URL como parámetro de consulta.

#Si no necesito una BD extensa, es mejor incluir los datos en el proyecto
#a partir de aquí las funcionalidades se hacen con consultas en excel
@app.get("/mean_year")
def precio_mean(year:str=Query(...)):
    try:
        df_year = df[df['Year'].astype(str)==year]
        resultados = df_year['Precio'].mean()
        return {'year': year, 'precio_promedio':round(resultados, 2) if not pd.isna(resultados) else None}
    except Exception as e:
        return{"Error":str(e)}
    
@app.get("/mean_precio_cp")
def mean_precio_cp(cp:str=Query(...)):
    try:
        dft = df[df['Year']==2025]
        filter_barrio= dft[dft['Consejo_Popular'].astype(str)==cp]
        mean_precio= filter_barrio['Precio'].mean()
        return {'Consejo_Popular':cp, 'precio_promedio':round(mean_precio, 2) if not pd.isna(mean_precio) else None}
    except Exception as e:
        return {'Error':str(e)}
    
@app.get("/frecuency")
def frecuencias():
    try:
        return {'Frecuencia_absoluta':frec_abs.to_dict(),'Frecuencia_relativa': frec_rel.to_dict()}
    except Exception as e:
        return {'Error':str(e)}
@app.get("/varianza")
def decriptiva():
    try:
        varz = df['Precio'].var()
        stand = df['Precio'].std()
        return {'Varianza': varz,'Standard_Deviation':stand}
    except Exception as e:
        return {'Error': str(e)}
@app.get("/graph")
def grafit():
    fig,ax= plt.subplots(figsize=(16,10))
    fre_gr.plot(kind='barh', edgecolor='black', ax=ax)
    dum = BytesIO()
    plt.tight_layout()
    plt.savefig(dum, format='png')
    dum.seek(0)
    plt.close(fig)
    return StreamingResponse(dum, media_type='image/png')