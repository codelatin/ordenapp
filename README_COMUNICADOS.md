# OrdenApp · Comunicados jerárquicos (MVP académico)

## Instalar sin perder la base de datos existente

1. Detén el servidor y haz una copia completa de tu carpeta `ordenapp_mvp`, especialmente `db.sqlite3`, `communications/migrations/` y `.venv` o `venv`.
2. Descomprime este ZIP. Copia su contenido **sobre** tu proyecto existente, sin borrar `db.sqlite3`, tu entorno virtual ni las migraciones ya generadas. No elimines la carpeta de migraciones de tu equipo.
3. En CMD, desde la carpeta del proyecto, activa tu entorno (`venv\Scripts\activate` o `.venv\Scripts\activate`, según el nombre real).
4. Ejecuta `pip install -r requirements.txt`, `python manage.py makemigrations communications`, `python manage.py migrate`, `python manage.py check` y `python manage.py runserver`.
5. Abre `/comunicados/`. Usa `director` o `comandante` para publicar y `soldado` para leer y confirmar.

## Prueba guiada

- En una ventana normal, accede con `comandante`, ve a **Comunicados → Nuevo** y selecciona la compañía Alfa.
- En una ventana de incógnito, accede con `soldado` y deja una página interna abierta: llegará un aviso WebSocket visible mientras la página esté abierta.
- En `soldado`, abre **Comunicados**, entra al mensaje y presiona **Confirmar recepción**.
- En `comandante`, abre el comunicado publicado y observa el seguimiento del destinatario.
- El director puede seleccionar cualquier unidad del prototipo; el comandante solo su unidad. Soldados no publican y nadie puede abrir un comunicado ajeno por URL.

## Restricciones conscientes

- Los destinatarios se determinan en el momento del envío; un cambio de unidad posterior no altera el historial.
- Los avisos WebSocket solo funcionan con la aplicación abierta. Redis no se usa: el canal en memoria sirve **solo en un proceso local**.
- Se confirma **recepción**, no cumplimiento de órdenes. Esto es un prototipo académico con datos ficticios, no un sistema militar certificado.
- El seed original no modifica contraseñas de cuentas existentes.
- Para añadir más usuarios de prueba, utiliza la administración de Django creando `User` y su `Profile`, con rol y unidad.
