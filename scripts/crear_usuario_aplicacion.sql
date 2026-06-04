USE master;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.sql_logins
    WHERE name = 'bot_facturas_app'
)
CREATE LOGIN bot_facturas_app
WITH PASSWORD = 'Cambiar_Esta_Clave_2026!';
GO

USE poc_bot_facturas;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.database_principals
    WHERE name = 'bot_facturas_app'
)
CREATE USER bot_facturas_app FOR LOGIN bot_facturas_app;
GO

REVOKE INSERT, UPDATE, DELETE ON SCHEMA::configuracion FROM bot_facturas_app;
REVOKE DELETE ON SCHEMA::operacion FROM bot_facturas_app;
GRANT SELECT ON SCHEMA::configuracion TO bot_facturas_app;
GRANT SELECT, INSERT, UPDATE ON SCHEMA::operacion TO bot_facturas_app;
GO
