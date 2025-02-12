
from serpapi import GoogleSearch
import pandas as pd
import dotenv
import os
import csv
# from transformers import pipeline
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline,
)

from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
#   import psycopg2

# --------------------------------------------------------------
dotenv.load_dotenv()
NEWS_FILE_PATH=os.getenv("NEWS_FILE_PATH")
AGG_FILE_PATH=os.getenv("AGG_FILE_PATH")
LAST30_FILE_PATH=os.getenv("LAST30_FILE_PATH")
print("**************************", NEWS_FILE_PATH," " , AGG_FILE_PATH)



# --------------------------------------------------------------

def e(fuentes) -> int:
    """
    Extrae los datos de Google News utilizando el API de SerpApi.
    Recorre las fuentes y guarda los resultados en un archivo CSV
    Devuelve: 0 si todo ha ido bien
    """
    print("Extract e()")

    
    SERPAPI_KEY=os.getenv("SERPAPI_KEY")
    open(NEWS_FILE_PATH, 'w').close() # Borra el contenido del archivo
    
    num_titles = 0
    for fuente in fuentes:
        params = {
            "engine": "google_news",
            "api_key": f"{SERPAPI_KEY}",
            # "publication_token": f"{fuentes[fuente]}",
            "topic_token": "CAAqIQgKIhtDQkFTRGdvSUwyMHZNRFp0YTJvU0FtVnpLQUFQAQ",
            "gl":"ES",
            "hl":"es",
        }
        print(f"Extrayendo noticias de {fuente} con tópico {fuentes[fuente]}...")
        search = GoogleSearch(params)
        results = search.get_dict()
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<")
        print(results)
        
        if 'news_results' not in results:
            print(f"No hay resultados para {fuente}")
            continue
        news_results = results["news_results"]
        
        
        
        with open(NEWS_FILE_PATH, 'a', newline='') as file:
            writer = csv.writer(file)
            for i in news_results:      
                titulo=None
                fuente=None
                # si no hay stories, no hay title
                if 'stories' in i:
                    titulo = i['stories'][0]['title'] 
                    fuente = i['stories'][0]['source']['name']        
                    
                else:
                    # Puede no  venir ni title ni stories
                    if 'title' in i:
                        titulo = i['title']
                    if 'source' in i:
                        fuente = i['source']['name']
                
                if titulo and len(titulo) > 30:
                    titulo=titulo.replace('"', "'")
                    writer.writerow([titulo, fuente,0])
                    num_titles += 1
    
    print(f"Extract e() -> {num_titles} noticias")
    return 0
# --------------------------------------------------------------

def t() -> int:
    """
    Transforma los datos del archivo CSV en un DataFrame de Pandas
    Devuelve: 0 si todo ha ido bien
    """
    print("Transform t()")
    df = pd.read_csv(NEWS_FILE_PATH, header=None, names=['titulo','fuente','clickbait'])

    tokenizerDOS = AutoTokenizer.from_pretrained("modelo/clickbait_es") #"taniwasl/clickbait_es")
    modelDOS = AutoModelForSequenceClassification.from_pretrained("modelo/clickbait_es") #("taniwasl/clickbait_es")
    nlp = TextClassificationPipeline(task = "text-classification",
                    model = modelDOS,
                    tokenizer = tokenizerDOS,
                    max_length = 25,
                    truncation=True,
                    add_special_tokens=True
                    )
    df['esclickbait'] = df['titulo'].apply(lambda x: [nlp(x)[0]['label'], nlp(x)[0]['score']])
    df[['cb','score']] = pd.DataFrame(df['esclickbait'].to_list())
    df['cb']=df['cb'].apply(lambda x: 'NO' if x=='NO Clickbait' else 'SI')
    df.drop(columns=['esclickbait','clickbait'], inplace=True)
    df.to_csv(NEWS_FILE_PATH,index=False)

    print("Transform t() -> Done")
    
    return 0
# --------------------------------------------------------------
def l() -> int:
    """
    Carga los datos del DataFrame en una base de datos SQLite
    Devuelve: 0 si todo ha ido bien
    """
    print("Load l()")
    r=0
    df=pd.read_csv(NEWS_FILE_PATH)
    
    try:
        conn = create_engine(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )   
        # session = scoped_session(sessionmaker(bind=conn))
    except Exception as e:
        print("Error de conexión:", e)
        return 1

    r=df.to_sql('cb_titulares', conn, if_exists='append', index=False, schema='public',chunksize=200 )
    print("l() ->", r, "filas insertadas")
    
    print("Generando fichero de datos de agregados...")
    open(AGG_FILE_PATH, 'w').close() # Borra el contenido del archivo
    df_agg=pd.read_sql_query("SELECT * FROM cb_view_agregados WHERE fecha > to_char((CURRENT_DATE - INTERVAL '30' day),'YYYY-MM-DD')", conn)
    df_agg.to_csv(AGG_FILE_PATH,index=False)
    
    print("Generando fichero de últimas noticias...")
    open(LAST30_FILE_PATH, 'w').close() # Borra el contenido del archivo
    df_agg=pd.read_sql_query("SELECT * FROM cb_titulares WHERE fec_creacion > CURRENT_DATE - INTERVAL '1' day", conn)
    df_agg.to_csv(LAST30_FILE_PATH,index=False)
    
    return 0

def etl():
    # Fuentes y tópico en Google News
    fuentes={
        # "El Mundo": "CAAqBwgKMMrnpQswovK9Aw",
        # "La Razón": "CAAiEMgwRAZ6a9xIqt_FOvel0ZUqFAgKIhDIMEQGemvcSKrfxTr3pdGV",
        # "Cadena Ser": "CAAqBwgKMJCd_gowyaKKAw", NO PIRULAN
        # "20 Minutos": "CAAqBwgKMJnElAswiIuqAw",
        # "ABC":"CAAqBwgKML3tuAswyojQAw",
        "EL PAIS": "CAAqJAgKIh5DQklTRUFnTWFnd0tDbVZzY0dGcGN5NWpiMjBvQUFQAQ", # "CAAqBwgKMMCZ_gowmpqKAw", 
        # "La Vanguardia": "CAAiEJfeIaNMtcmHNfDRR_Ef_1AqFAgKIhCX3iGjTLXJhzXw0UfxH_9Q",
        # "La Voz de Galicia": "CAAqBwgKMLzWggswqdONAw",
        # "Telecinco": "CAAiECFg1YKf7tBT5VX5h77PTxQqFAgKIhAhYNWCn-7QU-VV-Ye-z08U",
        # "La Sexta": "CAAiEF68L4M1bJgasbPp68zWMgwqFAgKIhBevC-DNWyYGrGz6evM1jIM",
        # "RTVE": "CAAqBwgKMJ6gqgswnqvCAw",
        # "El Confidencial": "CAAqBwgKMJ6gqgswnqvCAw",
        # "Antena3": "CAAiELe0XvGEu4_zWVl4gLdCuWoqFAgKIhC3tF7xhLuP81lZeIC3Qrlq",
        # "EL ESPAÑOL": "CAAqBwgKMPGypQswtL29Aw",
        # "COPE":"CAAqBwgKMKzKgAsw4-SMAw",
        # "Libertad Digital": "CAAqBggKMKHnKzDPnAE",
    }
    
    e(fuentes)
    t()
    # l()
    return 0
    
if __name__ == '__main__':
    r = etl()
    exit(r)