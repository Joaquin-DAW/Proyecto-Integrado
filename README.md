# Horarium

Horarium es una aplicación web para gestionar horarios, ausencias, guardias y partes diarios del profesorado de un centro educativo.

El proyecto permite importar el horario desde un archivo TXT, consultar horarios con filtros, registrar ausencias, generar partes PDF y enviarlos por correo al equipo directivo. También incluye una tarea automática que genera el parte diario en días lectivos.

## Tecnologías usadas

- Backend: Django y Django REST Framework.
- Frontend: Angular.
- Base de datos: PostgreSQL.
- Tareas en segundo plano: Redis, Celery y Celery Beat.
- PDF y correo: ReportLab y SMTP.
- Despliegue: Docker Compose. En producción se ha probado en AWS EC2.

## Requisitos previos

Para arrancar el proyecto en local solo hace falta tener instalado:

- Git.
- Docker Desktop.
- Un navegador web.

No es necesario instalar Python, Node, PostgreSQL ni Redis en el equipo, porque todos esos servicios se ejecutan en contenedores Docker.

## Instalación local

Clonar el repositorio:

```powershell
git clone https://github.com/Joaquin-DAW/Proyecto-Integrado.git
cd Proyecto-Integrado
```

Crear el archivo de variables de entorno a partir de la plantilla:

```powershell
copy .env.example .env
```

En Linux o macOS sería:

```bash
cp .env.example .env
```

El archivo `.env` contiene la configuración local del proyecto. No debe subirse a GitHub porque puede contener contraseñas, claves secretas o datos de correo.

## Arrancar la aplicación

Desde la carpeta principal del proyecto:

```powershell
docker compose up -d --build
```

La primera vez puede tardar unos minutos, porque Docker descarga imágenes, instala dependencias y compila el frontend.

Para comprobar que todo está levantado:

```powershell
docker compose ps
```

Deberían aparecer contenedores como:

- `horarium_frontend`
- `horarium_backend`
- `horarium_db`
- `horarium_redis`
- `horarium_celery_worker`
- `horarium_celery_beat`

## Crear usuario de prueba

Una vez arrancados los contenedores, crear el usuario administrador de demo:

```powershell
docker compose exec backend python manage.py setup_demo_admin
```

Credenciales por defecto:

- Email: `admin@iespoligonosur.org`
- Contraseña: `admin1234`

También se puede crear el usuario demo con otro correo:

```powershell
docker compose exec backend python manage.py setup_demo_admin --email correo@ejemplo.com --password admin1234
```

Este usuario es solo para pruebas. En una instalación real conviene crear usuarios propios y cambiar las contraseñas iniciales.

## Acceso a la aplicación

Con Docker levantado:

- Aplicación web: <http://localhost/>
- API backend: <http://localhost:8000/api/>
- Administración de Django: <http://localhost:8000/admin/>

Si el puerto 80 está ocupado por otro programa, el contenedor del frontend no podrá arrancar correctamente. En ese caso hay que liberar el puerto o cambiar el mapeo en `docker-compose.yml`.

## Primer uso recomendado

Después de iniciar sesión con el usuario de prueba:

1. Entrar en `Importar`.
2. Subir el archivo `backend/Datos_horarios.txt`.
3. Comprobar que se importan profesores y entradas de horario.
4. Revisar el buscador de horarios.
5. Crear una cuenta para algún profesor desde `Usuarios`.
6. Registrar una ausencia con descripción y tareas.
7. Revisar el `Panel diario`.
8. Generar un parte PDF desde `Partes`.
9. Enviar el parte por correo si SMTP está configurado.

## Configurar el correo

Por defecto, el proyecto puede funcionar sin enviar correos reales. En local, si se deja el backend de consola, los correos se imprimen en los logs del backend.

Para enviar correos reales hay que configurar SMTP en `.env`. Ejemplo con Gmail:

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

En Gmail no se usa la contraseña normal de la cuenta. Hay que crear una contraseña de aplicación y ponerla en `EMAIL_HOST_PASSWORD`.

Después de modificar `.env`, reiniciar los servicios que leen esa configuración:

```powershell
docker compose up -d --force-recreate backend celery_worker celery_beat
```

Los partes se envían a los usuarios activos con rol `EQUIPO_DIRECTIVO`.

## Parte diario automático

Horarium usa Celery Beat para programar la generación del parte diario. La tarea queda registrada al arrancar el backend, pero también se puede crear o actualizar manualmente:

```powershell
docker compose exec backend python manage.py setup_periodic_tasks
```

La tarea genera el parte general del IES de lunes a viernes a las 08:00, usando la zona horaria configurada en Django.

Para comprobar que la tarea existe:

```powershell
docker compose exec backend python manage.py shell -c "from django_celery_beat.models import PeriodicTask; [print(t.name, t.task, t.crontab) for t in PeriodicTask.objects.all()]"
```

## Comandos útiles

Ver logs del backend:

```powershell
docker compose logs --tail=100 backend
```

Comprobar la configuración de Django:

```powershell
docker compose exec backend python manage.py check
```

Ejecutar las pruebas del backend:

```powershell
docker compose exec backend python manage.py test
```

Reconstruir solo el frontend:

```powershell
docker compose build frontend
docker compose up -d frontend
```

Parar los contenedores:

```powershell
docker compose down
```

Parar los contenedores y borrar los datos locales de PostgreSQL:

```powershell
docker compose down -v
```

El comando con `-v` borra usuarios, horarios importados, ausencias y partes guardados en la base de datos local.

## Despliegue en AWS

El proyecto incluye un archivo `docker-compose.prod.yml` para desplegar Horarium en una instancia EC2 de AWS.

Resumen del proceso:

1. Crear una instancia EC2 con Ubuntu.
2. Abrir el puerto 80 para HTTP y el puerto 22 solo para la IP que vaya a conectarse por SSH.
3. Instalar Docker y Docker Compose en la instancia.
4. Clonar el repositorio.
5. Crear el archivo `.env` desde `.env.aws.example`.
6. Cambiar `SECRET_KEY`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `FRONTEND_URL` y la contraseña de PostgreSQL.
7. Levantar el proyecto:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Crear el usuario de prueba en AWS:

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py setup_demo_admin
```

En producción solo se expone el puerto 80. PostgreSQL, Redis y el backend quedan como servicios internos dentro de Docker.

## Problemas comunes

Si el login falla después de reconstruir el frontend, probar una recarga fuerte del navegador:

```text
Ctrl + F5
```

También puede ayudar abrir una ventana de incógnito para evitar tokens antiguos guardados en el navegador.

Si el usuario de prueba no funciona:

```powershell
docker compose exec backend python manage.py setup_demo_admin
```

Si los correos no llegan:

- comprobar que `.env` está guardado;
- revisar que `EMAIL_BACKEND` sea `django.core.mail.backends.smtp.EmailBackend`;
- usar una contraseña de aplicación si se utiliza Gmail;
- reiniciar `backend`, `celery_worker` y `celery_beat`;
- comprobar que existe al menos un usuario activo con rol `EQUIPO_DIRECTIVO`.

Si se cambia el archivo `.env` y no se nota el cambio, recrear los servicios afectados:

```powershell
docker compose up -d --force-recreate backend celery_worker celery_beat
```
