# Kimetrics Data Engineering Challenge

Este repositorio contiene la implementación de un modelo analítico tipo **Esquema Estrella** para retail, desplegado en **AWS RDS (PostgreSQL)**.

## Estructura

- `ddl/`: Scripts SQL para la creación del modelo dimensional.
- `data_generation/`: Script Python (ETL) para la generación y carga de datos sintéticos.
- `explain/`: Evidencia de optimización de consultas (Query Plans antes y después de indexación).
- `docs/`: Documentación arquitectónica, MER y Diccionario de Datos.

## Instrucciones de Ejecución

1. **Configuración:** Clonar el repositorio y configurar una instancia AWS RDS PostgreSQL (Free Tier).
2. **Dependencias:** Instalar librerías de Python: `pip install pandas sqlalchemy psycopg2-binary faker dotenv`.
3. **Despliegue DDL:** Ejecutar el script `ddl/schema.sql` en la base de datos para crear la estructura.
4. **Carga de Datos:** Configurar las credenciales en `data_generation/00_generate_data.py` y ejecutar el script para poblar las tablas.
5. **Validación:** Consultar la carpeta `explain/` para ver las métricas de rendimiento.

**Autor:** Luis Arturo Sánchez
