-- 1. Dimensión de Fecha (Se recomienda precargar con 5-10 años de datos)
CREATE TABLE dim_fecha (
    fecha_sk          INT PRIMARY KEY,
    fecha_completa    DATE NOT NULL UNIQUE,
    anio              SMALLINT NOT NULL,
    trimestre         SMALLINT NOT NULL,
    mes               SMALLINT NOT NULL,
    nombre_mes        VARCHAR(15) NOT NULL,
    dia               SMALLINT NOT NULL,
    dia_semana        VARCHAR(10) NOT NULL,
    es_fin_de_semana  BOOLEAN NOT NULL,
    es_feriado        BOOLEAN NOT NULL
);

-- 2. Dimensión de Tienda
CREATE TABLE dim_tienda (
	tienda_sk          SERIAL PRIMARY KEY UNIQUE,
    nombre_tienda      VARCHAR(100) NOT NULL,
    formato            VARCHAR(50) NOT NULL,
    ciudad             VARCHAR(100),
    estado             VARCHAR(100)
);

-- 3. Dimensión de Producto
CREATE TABLE dim_producto (
	producto_sk        SERIAL PRIMARY KEY UNIQUE,
    nombre_producto    VARCHAR(255) NOT NULL,
    marca              VARCHAR(100) NOT NULL,
    categoria          VARCHAR(100) NOT NULL,
    subcategoria       VARCHAR(100),
    precio_unitario    NUMERIC(10, 2)
);

-- 4. Tabla de Hechos - Ventas (Transactional Fact)
CREATE TABLE fact_ventas (
    venta_sk               BIGSERIAL PRIMARY KEY,
    fecha_sk               INT NOT NULL REFERENCES dim_fecha(fecha_sk),
    tienda_sk              INT NOT NULL REFERENCES dim_tienda(tienda_sk),
    producto_sk            INT NOT NULL REFERENCES dim_producto(producto_sk),
    
    -- Métricas
    cantidad		       INT NOT NULL,
    monto_total            NUMERIC(10, 2) NOT NULL,
    ticket_id              VARCHAR(50) NOT NULL,
    
    fecha_carga            TIMESTAMP NOT NULL,
    proceso_origen         VARCHAR(50)
);

-- 5. Tabla de Hechos - Inventario (Periodic Snapshot Fact)
-- Esto nos permite ver el estado del inventario en una fecha dada.
CREATE TABLE fact_inventario (
    inventario_sk          BIGSERIAL PRIMARY KEY,
    tienda_sk              INT NOT NULL REFERENCES dim_tienda(tienda_sk),
    producto_sk            INT NOT NULL REFERENCES dim_producto(producto_sk),
    fecha_sk               INT NOT NULL REFERENCES dim_fecha(fecha_sk),
    
    -- Métricas de Stock
    stock_disponible       INT NOT NULL,
    stock_actual           INT NOT NULL,
    stock_minimo           INT NOT NULL,
    dias_stock_restante    INT,
    
    fecha_carga            TIMESTAMP NOT NULL,
    proceso_origen         VARCHAR(50)
);


