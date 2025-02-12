
import pandas as pd
import dotenv
import os

from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
#   import psycopg2

# --------------------------------------------------------------
dotenv.load_dotenv()
PRO_FILE_PATH=os.getenv("PRO_FILE_PATH", "data/pro_news.csv")
CON_FILE_PATH=os.getenv("CON_FILE_PATH", "data/con_news.csv")
print("**************************", PRO_FILE_PATH," " , CON_FILE_PATH)



# --------------------------------------------------------------

def e(fuentes_pro, fuentes_con) -> int:    
    """
    Saca los datos de postgress
    Devuelve: 0 si todo ha ido bien
    """
    print("Extract e()")
    r=0
    
    try:
        conn = create_engine(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )   
        # session = scoped_session(sessionmaker(bind=conn))
    except Exception as e:
        print("Error de conexión:", e)
        return 1

    print("Generando fichero de noticias pro...")
    df_pro=pd.read_sql_query(f"SELECT titulo FROM cb_titulares WHERE fuente in ({fuentes_pro}) AND fec_creacion > CURRENT_DATE - INTERVAL '60' day", conn)
    df_pro.to_csv(PRO_FILE_PATH,index=False)

    print("Generando fichero de noticias con...")
    df_con=pd.read_sql_query(f"SELECT titulo FROM cb_titulares WHERE fuente in ({fuentes_con}) AND fec_creacion > CURRENT_DATE - INTERVAL '60' day", conn)
    df_con.to_csv(CON_FILE_PATH,index=False)
    
    print(f"Extract e() -> Pro_news: {df_pro.shape[0]}   Con_news: {df_con.shape[0]}")
    return 0
# --------------------------------------------------------------

def t() -> int:
    """
    Transforma los datos del archivo CSV en un DataFrame de Pandas
    Devuelve: 0 si todo ha ido bien
    """
    print("Transform t()")

    print("Transform t() -> Done")
    
    return 0
# --------------------------------------------------------------
def l() -> int:

    print("Load l()")

    print("Load l() -> Done")
    
    return 0

def etl():
    # Fuentes y tópico en Google News
    fuentes_pro="'EL PAIS','RTVE'"
    fuentes_con="'EL ESPAÑOL','El Mundo','La Razón','Libertad Digital','La Voz de Galicia'"
    
    e(fuentes_pro, fuentes_con)
    t()
    l()
    return 0
    
if __name__ == '__main__':
    r = etl()
    exit(r)