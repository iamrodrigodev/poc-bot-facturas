USE poc_bot_facturas;
GO

IF NOT EXISTS (
    SELECT 1
    FROM configuracion.pagina_fuente
    WHERE pagina_fuente_url = 'https://samplelib.com/sample-zip.html'
)
BEGIN
    INSERT INTO configuracion.pagina_fuente (
        pagina_fuente_nombre,
        pagina_fuente_url,
        pagina_fuente_activa,
        fecha_creacion
    )
    VALUES (
        'samplelib',
        'https://samplelib.com/sample-zip.html',
        1,
        GETDATE()
    );
END;
GO
