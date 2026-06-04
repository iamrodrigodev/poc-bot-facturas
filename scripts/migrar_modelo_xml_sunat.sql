USE poc_bot_facturas;
GO

SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
GO

IF COL_LENGTH('operacion.archivo_xml', 'xml_rfc_receptor') IS NOT NULL
   AND OBJECT_ID(N'operacion.envio_bitacora', N'U') IS NOT NULL
    DROP TABLE operacion.envio_bitacora;
GO

IF COL_LENGTH('operacion.archivo_xml', 'xml_rfc_receptor') IS NOT NULL
    DROP TABLE operacion.archivo_xml;
GO

IF COL_LENGTH('configuracion.cliente', 'cliente_rfc') IS NOT NULL
    EXEC sp_rename
        'configuracion.cliente.cliente_rfc',
        'cliente_ruc',
        'COLUMN';
GO

IF EXISTS (
    SELECT 1
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'configuracion'
      AND TABLE_NAME = 'cliente'
      AND COLUMN_NAME = 'cliente_ruc'
      AND (
          DATA_TYPE <> 'varchar'
          OR CHARACTER_MAXIMUM_LENGTH <> 11
      )
)
BEGIN
    IF EXISTS (
        SELECT 1
        FROM sys.indexes
        WHERE name = 'uq_cliente_ruc'
    )
        DROP INDEX uq_cliente_ruc ON configuracion.cliente;

    ALTER TABLE configuracion.cliente
    ALTER COLUMN cliente_ruc varchar(11) NULL;
END;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'uq_cliente_ruc'
)
CREATE UNIQUE INDEX uq_cliente_ruc
ON configuracion.cliente (cliente_ruc)
WHERE cliente_ruc IS NOT NULL;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.check_constraints
    WHERE name = 'ck_cliente_ruc_longitud'
)
ALTER TABLE configuracion.cliente
ADD CONSTRAINT ck_cliente_ruc_longitud
CHECK (cliente_ruc IS NULL OR LEN(cliente_ruc) = 11);
GO
