IF DB_ID(N'poc_bot_facturas') IS NULL
BEGIN
    CREATE DATABASE poc_bot_facturas;
END;
GO

USE poc_bot_facturas;
GO

IF SCHEMA_ID(N'configuracion') IS NULL
BEGIN
    EXEC(N'CREATE SCHEMA configuracion');
END;
GO

IF SCHEMA_ID(N'operacion') IS NULL
BEGIN
    EXEC(N'CREATE SCHEMA operacion');
END;
GO
