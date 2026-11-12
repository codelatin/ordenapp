# OrdenApp: estructura jerárquica académica v2

Este ZIP parte de la versión de OrdenApp con comunicados. **No incluye datos reales ni base de datos**.

## Instalación segura en tu equipo (CMD)

1. Detén Django (`Ctrl+C`). Haz una copia COMPLETA de `C:\Users\USER\ordenapp_mvp`.
2. Descomprime el ZIP. Copia su contenido a tu carpeta de proyecto y reemplaza los archivos de código; **NO borres `db.sqlite3`, `venv`, `.venv` ni la carpeta `communications/migrations` existente**. No copies una migración inicial nueva sobre tus migraciones existentes.
3. Si utilizas CMD y tu entorno se llama `venv`:

```bat
cd C:\Users\USER\ordenapp_mvp
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations communications
python manage.py migrate
python manage.py seed_demo
python manage.py check
python manage.py test communications
python manage.py runserver
```

4. Abre `http://127.0.0.1:8000/jerarquia/` y prueba los comunicados y el chat en dos ventanas.
5. Cuentas nuevas: `subdirector`, `vicerrector`, `batallon`, `cuadro`, `comandante_bravo`, `soldado_bravo`, `cuadro_charlie`, `soldado_charlie`. Permanecen: `director`, `comandante`, `soldado`.
   Contraseña inicial para cuentas recién creadas: `DemoOrden2026!`. Las cuentas existentes conservan su contraseña.
6. **Solo si necesitas restablecer contraseñas de demo local:** `python manage.py seed_demo --reset-passwords`.

## Jerarquía de ejemplo (no validada oficialmente)

- Coronel director: comunicación y publicación a cualquier compañía.
- Coronel subdirector: comunicación y publicación a cualquier compañía.
- Coronel vicerrector académico: comunicación institucional amplia y publicación académica a compañías (regla simulada).
- Teniente coronel comandante de batallón: comunicación con compañías subordinadas; publicación a sus compañías.
- Comandante de compañía: mensajes con su personal, escalamiento hacia mandos superiores y comunicados solo a su compañía.
- Cuadro de compañía: mensajes al personal de su compañía, y comunicados solo a su compañía.
- Soldado bachiller: recibe y confirma comunicados; mensajes a su comandante, cuadro y superiores autorizados.

La visibilidad de usuarios en el organigrama NO significa permiso automático para contactarlos. Los permisos se verifican en el servidor en cada envío. La restricción para publicar comunicados se aplica a unidades de tipo compañía. El mando superior y la vicerrectoría se tratan como excepciones globales **solo en la demo**.

## Importante

No utilices nombres, números, órdenes o planes operacionales reales. No es un sistema acreditado para información sensible. `SECRET_KEY`, `DEBUG` y los accesos de ejemplo son solo locales.

`seed_demo` es idempotente con usuarios y unidades: no crea duplicados ni modifica contraseñas existentes por defecto. Sí reasigna las cuentas de prueba a sus unidades/roles definidos, por lo que NO debe ejecutarse en un proyecto que ya gestione usuarios institucionales reales.
