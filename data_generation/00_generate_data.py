import pandas as pd
import numpy as np
from faker import Faker
from sqlalchemy import create_engine
import datetime
import random
import os
import dotenv

# Cargar variables de entorno
dotenv.load_dotenv()

# --- CONFIGURACIÓN (SUSTITUYE CON TUS DATOS DE RDS) ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "").strip(),
    "port": os.getenv("DB_PORT", "5432").strip(),
    "database": os.getenv("DB_NAME", "").strip(),
    "user": os.getenv("DB_USER", "").strip(),
    "password": os.getenv("DB_PASSWORD", "").strip(),
}

# Validar que las variables de entorno estén configuradas
print("=== Configuración de Conexión ===")
print(f"Host: {DB_CONFIG['host']}")
print(f"Puerto: {DB_CONFIG['port']}")
print(f"Base de datos: {DB_CONFIG['database']}")
print(f"Usuario: {DB_CONFIG['user']}")
print(f"Password: {'*' * len(DB_CONFIG['password'])}\n")
print("=" * 35)

if not all(
    [DB_CONFIG["host"], DB_CONFIG["database"], DB_CONFIG["user"], DB_CONFIG["password"]]
):
    print("ERROR: Faltan variables de entorno en el archivo .env")
    print(
        "Verifica que DB_HOST, DB_NAME, DB_USER y DB_PASSWORD estén configuradas correctamente"
    )
    exit(1)

# Construir URL de conexión
connection_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

engine = create_engine(connection_url)

print("\nProbando conexión...")
try:
    with engine.connect() as connection:
        from sqlalchemy import text

        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()
        print(f"✓ Conexión a RDS exitosa!")
        print(f"✓ Versión de PostgreSQL: {version[0][:50]}...\n")
except Exception as e:
    print(
        f"""\n❌ Error al conectar a RDS:
                    Tipo de error: {type(e).__name__}
                    Mensaje: {e}"""
    )
    exit(1)

# --- PARÁMETROS DE GENERACIÓN DE DATOS ---
NUM_TIENDAS = 300
NUM_PRODUCTOS = 100
YEARS_HISTORY = 5
TRANSACCIONES_DIARIAS_PROM = 150 

fake = Faker("es_MX")


def generate_dim_fecha(start_year, end_year):
    print("\nGenerando Dimensión Fecha...")
    start_date = datetime.date(start_year, 1, 1)
    end_date = datetime.date(end_year, 12, 31)
    date_range = pd.date_range(start_date, end_date)

    df = pd.DataFrame({"fecha_completa": date_range})
    df["fecha_sk"] = df["fecha_completa"].dt.strftime("%Y%m%d").astype(int)
    df["fecha_completa"] = pd.to_datetime(df["fecha_completa"])
    df["anio"] = df["fecha_completa"].dt.year
    df["trimestre"] = df["fecha_completa"].dt.quarter
    df["mes"] = df["fecha_completa"].dt.month
    df["nombre_mes"] = df["fecha_completa"].dt.month_name()
    df["dia"] = df["fecha_completa"].dt.day
    df["dia_semana"] = df["fecha_completa"].dt.day_name()
    df["es_fin_de_semana"] = df["fecha_completa"].dt.dayofweek >= 5
    df["es_feriado"] = df["fecha_completa"].isin(
        [
            datetime.date(start_year + i, m, d)
            for i in range(end_year - start_year + 1)
            for m, d in [(1, 1), (5, 1), (9, 16), (11, 20), (12, 25)]
        ]
    )

    return df


def generate_dim_tienda(n):
    print("\nGenerando Dimensión Tienda...")
    data = []
    formatos = [
        "Supermercado",
        "Hipermercado",
        "Express",
        "Tienda de Barrio",
        "Conveniencia",
        "Outlet",
        "Especializada",
    ]
    for _ in range(n):
        data.append(
            {
                "nombre_tienda": f"Tienda_{fake.city()}",
                "formato": random.choice(formatos),
                "ciudad": fake.city(),
                "estado": fake.state(),
            }
        )
    return pd.DataFrame(data)


def generate_dim_producto(n):
    print("\nGenerando Dimensión Producto...")
    data = []
    categorias = ["Electrónica", "Hogar", "Ropa", "Alimentos", "Juguetes"]
    for _ in range(n):
        cat = random.choice(categorias)
        data.append(
            {
                "nombre_producto": f"{fake.word().capitalize()} {fake.word().capitalize()}",
                "marca": fake.company(),
                "categoria": cat,
                "subcategoria": f"{cat}_{fake.word().capitalize()}",
                "precio_unitario": round(random.uniform(10, 5000), 2),
            }
        )
    return pd.DataFrame(data)


def generate_fact_ventas(df_dates, df_stores, df_prods):
    print("\nGenerando Fact Ventas (Esto puede tardar)...")

    num_rows = len(df_dates) * TRANSACCIONES_DIARIAS_PROM

    fechas_sample = np.random.choice(df_dates["fecha_sk"], num_rows)
    tiendas_sample = np.random.choice(df_stores["tienda_sk"], num_rows)
    prods_sample = np.random.choice(df_prods["producto_sk"], num_rows)

    # Creamos DF base
    df = pd.DataFrame(
        {
            "venta_sk": range(1, num_rows + 1),
            "fecha_sk": fechas_sample,
            "tienda_sk": tiendas_sample,
            "producto_sk": prods_sample,
            "cantidad": np.random.randint(1, 5, num_rows),
            "ticket_id": [fake.uuid4()[:12] for _ in range(num_rows)],
            "fecha_carga": datetime.datetime.now(),
            "proceso_origen": "ETL_Generado",
        }
    )


    df = df.merge(
        df_prods[["producto_sk", "precio_unitario"]],
        on="producto_sk",
    )
    df["monto_total"] = df["cantidad"] * df["precio_unitario"]

    return df[
        [
            "venta_sk",
            "fecha_sk",
            "tienda_sk",
            "producto_sk",
            "cantidad",
            "monto_total",
            "ticket_id",
            "fecha_carga",
            "proceso_origen",
        ]
    ]


def load_to_rds(df, table_name):
    print(f"Cargando tabla: {table_name} a AWS RDS...")
    df.to_sql(
        table_name,  # nombre de la tabla
        engine,  # motor de conexión
        if_exists="append",  # comportamiento si la tabla ya existe
        index=False,  # no incluir el índice del DataFrame como columna
        chunksize=1000,  # tamaño de los lotes para la inserción
    )
    print(f"-> {len(df)} registros cargados en {table_name}.")


def main():
    # 1. Generar Dataframes
    current_year = datetime.datetime.now().year
    df_fecha = generate_dim_fecha(current_year - YEARS_HISTORY, current_year)
    df_tienda = generate_dim_tienda(NUM_TIENDAS)
    df_producto = generate_dim_producto(NUM_PRODUCTOS)

    # Cargar Dimensiones primero (para integridad referencial)
    load_to_rds(df_fecha, "dim_fecha")
    load_to_rds(df_tienda, "dim_tienda")
    load_to_rds(df_producto, "dim_producto")

    # Recuperar las tablas con sus SKs autogenerados
    print("\nRecuperando claves generadas...")
    df_tienda = pd.read_sql("SELECT * FROM dim_tienda", engine)
    df_producto = pd.read_sql("SELECT * FROM dim_producto", engine)

    # 2. Generar y Cargar Facts
    df_ventas = generate_fact_ventas(df_fecha, df_tienda, df_producto)
    load_to_rds(df_ventas, "fact_ventas")

    # (Opcional) Generar Inventario simplificado
    print("Generando inventario dummy...")
    # Inventario snapshot para hoy
    df_inv = pd.DataFrame(
        {
            "inventario_sk": range(1, NUM_TIENDAS + 1),
            "tienda_sk": df_tienda["tienda_sk"],
            "producto_sk": np.random.choice(df_producto["producto_sk"], NUM_TIENDAS),
            "fecha_sk": [int(datetime.datetime.now().strftime("%Y%m%d"))] * NUM_TIENDAS,
            "stock_disponible": np.random.randint(0, 100, NUM_TIENDAS),
            "stock_actual": np.random.randint(0, 100, NUM_TIENDAS),
            "stock_minimo": 10,
            "dias_stock_restante": np.random.randint(1, 30, NUM_TIENDAS),
            "fecha_carga": datetime.datetime.now(),
            "proceso_origen": "ETL_Generado",
        }
    )
    load_to_rds(df_inv, "fact_inventario")

    print("\n¡Proceso ETL completado con éxito!")


if __name__ == "__main__":
    main()
