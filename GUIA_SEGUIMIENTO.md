# OrdenApp — módulo de seguimiento de comunicados (v3)

Esta actualización parte de `OrdenApp_Jerarquia_EMSUB_v2` y **conserva las tablas actuales**. El seguimiento usa `BulletinReceipt.read_at` y `BulletinReceipt.confirmed_at` existentes; no agrega modelos ni exige migraciones nuevas por sí mismo.

## Instalar con seguridad en Windows (CMD)

1. Detén el servidor con `Ctrl+C`.
2. Haz una copia de seguridad de la carpeta `C:\Users\USER\ordenapp_mvp` completa, especialmente `db.sqlite3` y `communications/migrations`.
3. Descomprime el ZIP y copia sus carpetas `communications`, `config`, `templates` y `static` a tu proyecto, reemplazando los archivos de código. **No borres ni reemplaces** `db.sqlite3`, `venv`, `.venv` o `communications/migrations`.
4. Ejecuta:

```bat
cd C:\Users\USER\ordenapp_mvp
venv\Scripts\activate
python manage.py check
python manage.py test communications
python manage.py runserver
```

Si el entorno se llama `.venv`, utiliza `.venv\Scripts\activate`.

## Probar

1. Inicia sesión como `comandante` y abre **Comunicados**.
2. En **Publicados**, abre un comunicado creado por esa cuenta.
3. Selecciona **VER SEGUIMIENTO COMPLETO**. Alternativamente navega a `/comunicados/ID/seguimiento/` usando el ID real del comunicado.
4. Aparecerán métricas de destinatarios, pendientes de lectura, leídos sin confirmar y confirmados, barras de porcentaje, filtros y exportación CSV.
5. Desde una ventana de incógnito inicia sesión como `soldado`. Lee y confirma el comunicado.
6. En la sesión del comandante pulsa **ACTUALIZAR** y observa los contadores. Prueba los filtros por estado y el CSV.
7. Para comprobar seguridad, intenta abrir la URL de seguimiento con la sesión `soldado`: debe devolver 404.

## Semántica de los estados

- **Sin leer**: `read_at` y `confirmed_at` vacíos.
- **Leído sin confirmar**: `read_at` definido y `confirmed_at` vacío.
- **Confirmado**: `confirmed_at` definido, independiente de si la sesión sigue abierta.

La suma de sin leer + leído sin confirmar + confirmado es el total. El porcentaje de lectura incluye confirmados. **La creación del registro de destinatario no demuestra entrega efectiva al dispositivo**. No se afirma confirmación de entrega WebSocket ni garantías institucionales.

## Seguridad y alcance

Solo el emisor accede al seguimiento nominativo y a su CSV. Un receptor solo puede abrir y confirmar su propia recepción. Esta es una demostración académica con datos ficticios: no usar para información real sensible.
