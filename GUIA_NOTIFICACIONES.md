# OrdenApp v4 — Notificaciones en tiempo real

## Funcionalidad
- Campana global con cantidad de comunicados **sin leer**.
- Bandeja desplegable con los 6 comunicados recibidos más recientes (vínculos hacia cada comunicado).
- En el dashboard: no leídos, pendientes de confirmar y acuses pendientes de publicaciones propias.
- Nuevo comunicado: evento WebSocket al destinatario + actualización de contadores.
- Primera lectura y confirmación: evento al emisor para refrescar el estado; confirmación actualiza también la sesión del destinatario.
- Recuperación tras desconexión: reconexión automática con espera creciente y consulta de estado al reconectar o volver a la pestaña.
- No incluye push con navegador cerrado ni certificaciones militares.

## Instalación segura en tu proyecto existente
1. Cierra `runserver`; copia toda la carpeta actual y el archivo `db.sqlite3`.
2. Descomprime el ZIP. Copia el contenido nuevo del proyecto a `C:\Users\USER\ordenapp_mvp`, reemplazando código pero **no** `db.sqlite3`, `venv`/`.venv` ni migraciones preexistentes.
3. Ejecuta desde CMD con el entorno activo:
   ```cmd
   python manage.py check
   python manage.py test communications
   python manage.py runserver
   ```
4. Inicia sesión con `comandante` en ventana normal y `soldado` en incógnito.
5. El comandante publica un comunicado en Alfa: el soldado recibe aviso y sube contador de campana sin recargar.
6. El soldado abre comunicado: cambia de sin leer a pendiente de confirmar.
7. El soldado confirma: el comandante ve actualizado el contador de acuses pendientes; en la vista de seguimiento pulsa Actualizar si la mantiene abierta.

No se requieren migraciones: sólo se utilizan `Bulletin` y `BulletinReceipt` ya existentes.

### Detalles técnicos
- `GET /notificaciones/estado/` requiere sesión y devuelve solamente datos autorizados del usuario actual.
- `/ws/bulletins/`: eventos `new_bulletin` y `bulletin_progress`.
- `static/js/notifications.js`: acceso al DOM mediante `textContent`, sin inyectar HTML de mensajes.
- `InMemoryChannelLayer` sirve únicamente si Django corre en **un solo proceso**, para esta demostración local. Con múltiples procesos se necesita Redis.
