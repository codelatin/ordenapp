# OrdenApp — MVP académico (v0.1)

Demostración ficticia de chat 1 a 1 con permisos jerárquicos y actualizaciones WebSocket. **No utilizar con datos institucionales reales.**

## Requisitos
- Python 3.12 recomendado
- Conexión a Internet para cargar Bootstrap por CDN (o sustituir por archivo local)

## Instalar en Windows PowerShell
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations communications
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
En Linux/macOS usar `python3 -m venv .venv` y `source .venv/bin/activate`.

Abrir http://127.0.0.1:8000/login/ y entrar como `comandante` en una ventana y `soldado` en incógnito. Las cuentas de ejemplo `director`, `comandante`, `soldado` usan contraseña `DemoOrden2026!` cuando son creadas por primera vez.

## Qué incluye
- Autenticación Django y panel de administración nativo (crear superusuario con `python manage.py createsuperuser`)
- Roles ficticios: dirección, mando de compañía, soldado
- Unidad organizativa
- Autorización de destinatarios y revalidación de permisos al enviar
- Mensajes persistidos en SQLite
- Chat WebSocket uno a uno con Channels
- Interfaz web responsive simple

## Limitaciones intencionales
- `InMemoryChannelLayer` solo para **un proceso** de desarrollo. Para múltiples procesos usar Redis.
- No incluye órdenes formales, confirmaciones de lectura, chats grupales, push, pruebas automatizadas ni auditoría; son trabajo posterior.
- `DEBUG=True`, clave secreta de ejemplo, contraseñas de prueba y validadores desactivados: **nunca publicar** esta configuración.
- Solo se usa información y usuarios inventados. La jerarquía es ilustrativa.
- Las pantallas no actualizan automáticamente la lista de contactos; el chat activo sí recibe eventos.

## Para continuar
1. Añadir tests de las reglas de `can_message`.
2. Añadir grupos por compañía y mensajes institucionales.
3. Añadir notificaciones visibles en el dashboard y confirmación de lectura.
4. Cambiar a variables de entorno, contraseñas seguras y Redis/PostgreSQL para cualquier piloto supervisado.


## Home integrado (2026-11)
- `http://127.0.0.1:8000/` muestra la nueva landing page estilo Tactical Command Matrix.
- `http://127.0.0.1:8000/login/` abre el login actual.
- Tras iniciar sesión se abre `/inbox/` para conservar el flujo de mensajería existente.
- El diseño está en `templates/home.html` y mantiene Tailwind CDN y Google Fonts (requiere conexión a Internet).
- El archivo `DESIGN_SYSTEM.md` contiene la referencia visual proporcionada.
- Los mensajes, alertas y otras tarjetas en la landing son solo ilustrativos; la página no implementa por sí misma nuevas funciones.
- Se eliminaron/reformularon afirmaciones de certificaciones, cifrado extremo a extremo o prestaciones no presentes en el MVP.
- Ningún archivo de base de datos está incluido; conserva tu `db.sqlite3` anterior en tu computador.

### Actualizar proyecto ya instalado
Haz una copia de seguridad de tu carpeta actual y de `db.sqlite3`. Copia los archivos del ZIP a tu carpeta `ordenapp_mvp`, sin borrar tu base de datos. Reinicia `python manage.py runserver`.


## Dashboard táctico integrado (v1.1)

- `/dashboard/` es el panel privado que se abre después de iniciar sesión.
- Mantiene la identidad visual del Home: Barlow Condensed, Inter, JetBrains Mono; fondos #0d141a y #192126, verde #b9cda2, naranja #ff6a00.
- Métricas calculadas a partir de mensajes de la cuenta autenticada. `Sin leer` se actualiza al abrir la conversación desde la vista HTTP; una conversación abierta que recibe mensajes nuevos no confirma automáticamente la lectura.
- Accesos rápidos a conversaciones, historial reciente, unidad y cargo.
- Las rutas `/inbox/`, `/chat/<id>/`, `/admin/` y `/` continúan disponibles.
- En Windows: `.venv\Scripts\activate`, `pip install -r requirements.txt`, `python manage.py migrate`, `python manage.py runserver`. No necesitas borrar ni reemplazar `db.sqlite3`.
- Si la versión anterior ya estaba instalada, **copia los archivos del nuevo ZIP sobre el proyecto existente**, pero conserva el archivo SQLite local.
- Versión demostrativa: sin métricas simuladas, sin garantías de cifrado especial, sin Web Push y sin auditoría inmutable.
