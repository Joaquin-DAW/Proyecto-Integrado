# Horarium

Aplicación web para gestionar horarios, ausencias del profesorado, guardias y partes de ausencias del IES Polígono Sur.

El objetivo principal es que el equipo directivo pueda importar el horario del centro, registrar ausencias, ver qué profesorado de guardia está disponible y generar un parte común en PDF que también se puede enviar por correo.

## Tecnologías

- `backend`: API con Django REST Framework.
- `frontend`: interfaz web con Angular.
- `PostgreSQL`: base de datos.
- `Redis` y `Celery`: tareas en segundo plano y generación programada de partes.
- `Docker Compose`: arranque completo del proyecto.

## Funcionalidades principales

- Importación del horario desde un fichero `.txt`.
- Consulta de horarios por profesor, día, grupo, asignatura y aula.
- Gestión de usuarios y roles: profesorado y equipo directivo.
- Registro de ausencias propias por parte del profesorado.
- Registro de ausencias de cualquier profesor por parte del equipo directivo.
- Campo de tareas asociado a la ausencia, para indicar qué debe hacer el alumnado durante la guardia.
- Panel diario para equipo directivo con ausencias, guardias disponibles y profesorado de guardia ausente.
- Clasificación de guardias por módulo A, módulo B o general.
- Generación de partes de ausencia en PDF.
- Envío del parte por email a los usuarios activos del equipo directivo.
- Recuperación de contraseña por correo si SMTP está configurado.

## Requisitos

Para arrancar el proyecto en local hace falta:

- Docker Desktop instalado y abierto.
- Git, si se clona desde GitHub.

No hace falta instalar Python, Node, PostgreSQL ni Redis en el ordenador si se usa Docker.

## Configuración inicial

Desde la carpeta del proyecto, copiar la plantilla de entorno:

```powershell
cd horarium
copy .env.example .env
```

El archivo `.env` contiene la configuración local. No debe subirse a GitHub porque puede contener contraseñas.

## Arrancar el proyecto

Desde la carpeta `horarium`:

```powershell
docker compose up -d --build
```

La primera vez puede tardar unos minutos porque descarga imágenes y compila el frontend.

Comprobar que los contenedores están levantados:

```powershell
docker compose ps
```

Deberían aparecer servicios como `backend`, `frontend`, `db`, `redis`, `celery_worker` y `celery_beat`.

## Usuario de prueba

Para crear o resetear un usuario administrador de demo:

```powershell
docker compose exec backend python manage.py setup_demo_admin
```

Credenciales por defecto:

- Email: `admin@iespoligonosur.org`
- Contraseña: `admin1234`

También se puede crear otro usuario de equipo directivo con un email concreto:

```powershell
docker compose exec backend python manage.py setup_demo_admin --email correo@ejemplo.com --password admin1234
```

Este usuario es solo para pruebas locales. En un entorno real habría que crear usuarios reales y cambiar contraseñas.

## URLs principales

- Aplicación web: <http://localhost/>
- API backend: <http://localhost:8000/api/>
- Admin de Django: <http://localhost:8000/admin/>

## Primer uso recomendado

1. Entrar en <http://localhost/> con el usuario de prueba.
2. Ir a `Importar Horario`.
3. Subir el fichero `backend/Datos_horarios.txt`.
4. Revisar que se crean profesores y entradas de horario.
5. Probar el buscador de horarios.
6. Crear una cuenta para algún profesor desde `Gestión de Usuarios`.
7. Registrar una ausencia con descripción y tareas.
8. Revisar el `Panel diario` de esa fecha.
9. Generar un parte PDF desde `Partes`.
10. Enviar el parte por email si SMTP está configurado.

## Configurar envío de correo

Por defecto, el proyecto puede funcionar sin enviar correos reales. Para pruebas reales se puede configurar SMTP en `.env`.

Ejemplo con Gmail:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=cuenta-del-proyecto@gmail.com
EMAIL_HOST_PASSWORD=contraseña-de-aplicacion
DEFAULT_FROM_EMAIL=Horarium <cuenta-del-proyecto@gmail.com>
FRONTEND_URL=http://localhost
```

En Gmail no se debe usar la contraseña normal de la cuenta. Lo recomendable es crear una contraseña de aplicación y ponerla en `EMAIL_HOST_PASSWORD`.

Después de cambiar el `.env`, reiniciar los servicios que leen configuración:

```powershell
docker compose up -d --force-recreate backend celery_worker celery_beat
```

El parte se envía a los usuarios con rol `EQUIPO_DIRECTIVO` que estén activos y tengan email.

## Parte diario automático

Celery Beat registra una tarea para generar el parte común de ausencias en días lectivos.

Para crear o actualizar esa tarea manualmente:

```powershell
docker compose exec backend python manage.py setup_periodic_tasks
```

El flujo automático usa el parte común del IES. Los partes por módulo A/B siguen disponibles para generación manual.

## Comprobaciones útiles

Revisar configuración general de Django:

```powershell
docker compose exec backend python manage.py check
```

Ejecutar pruebas del backend:

```powershell
docker compose exec backend python manage.py test
```

Reconstruir solo el frontend si se cambian pantallas Angular:

```powershell
docker compose build frontend
docker compose up -d frontend
```

## Parar el proyecto

Para parar los contenedores:

```powershell
docker compose down
```

Para parar y borrar también los datos de la base de datos local:

```powershell
docker compose down -v
```

`-v` elimina los datos guardados en PostgreSQL, incluyendo usuarios, horarios importados, ausencias y partes.

## Problemas comunes

Si el login falla después de reconstruir el frontend, probar una recarga fuerte:

```text
Ctrl + F5
```

También se puede abrir una ventana de incógnito para evitar tokens antiguos guardados en el navegador.

Si el usuario de prueba no funciona:

```powershell
docker compose exec backend python manage.py setup_demo_admin
```

Si el envío de email falla, comprobar:

- que `.env` está guardado;
- que se reinició `backend`, `celery_worker` y `celery_beat`;
- que `EMAIL_BACKEND` es `django.core.mail.backends.smtp.EmailBackend`;
- que la contraseña de Gmail es una contraseña de aplicación;
- que hay al menos un usuario activo con rol `EQUIPO_DIRECTIVO`.
