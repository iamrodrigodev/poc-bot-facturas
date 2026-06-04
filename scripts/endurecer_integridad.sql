USE poc_bot_facturas;
GO

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'ck_archivo_bitacora_descarga_consistente'
)
ALTER TABLE operacion.archivo_bitacora
ADD CONSTRAINT ck_archivo_bitacora_descarga_consistente
CHECK (
    archivo_bitacora_descarga_ok = 0
    OR (
        archivo_bitacora_nombre_fisico IS NOT NULL
        AND archivo_bitacora_ruta_descarga IS NOT NULL
    )
);
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'ck_archivo_bitacora_descompresion_consistente'
)
ALTER TABLE operacion.archivo_bitacora
ADD CONSTRAINT ck_archivo_bitacora_descompresion_consistente
CHECK (
    archivo_bitacora_descompresion_ok = 0
    OR (
        archivo_bitacora_descarga_ok = 1
        AND archivo_bitacora_ruta_extraccion IS NOT NULL
    )
);
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'ck_archivo_bitacora_envio_consistente'
)
ALTER TABLE operacion.archivo_bitacora
ADD CONSTRAINT ck_archivo_bitacora_envio_consistente
CHECK (
    archivo_bitacora_envio_ok = 0
    OR archivo_bitacora_descompresion_ok = 1
);
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'uq_archivo_bitacora_descarga_exitosa'
)
CREATE UNIQUE INDEX uq_archivo_bitacora_descarga_exitosa
ON operacion.archivo_bitacora (archivo_tipo_id)
WHERE archivo_bitacora_descarga_ok = 1;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'ck_envio_bitacora_estado'
)
ALTER TABLE operacion.envio_bitacora
ADD CONSTRAINT ck_envio_bitacora_estado
CHECK (envio_bitacora_estado IN ('enviado', 'error'));
GO
