-- OPTIMIZACIÓN: Creación de Índices B-Tree
-- Justificación: Aceleramos los JOINS con las dimensiones principales.

CREATE INDEX idx_ventas_tienda_fecha ON fact_ventas (tienda_sk, fecha_sk);

CREATE INDEX idx_inventario_tienda_fecha ON fact_inventario (tienda_sk, fecha_sk);

CREATE INDEX idx_ventas_tienda ON fact_ventas (tienda_sk);

CREATE INDEX idx_ventas_producto ON fact_ventas (producto_sk);

CREATE INDEX idx_ventas_fecha ON fact_ventas (fecha_sk);

CREATE INDEX idx_ventas_tienda_fecha ON fact_ventas (tienda_sk, fecha_sk);

CREATE INDEX idx_ventas_ticket ON fact_ventas (ticket_id);

-- ANALYZE fact_ventas;