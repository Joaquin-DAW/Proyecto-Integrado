# Horarium

Aplicacion web para gestionar horarios, ausencias del profesorado y partes de ausencias en PDF para el IES Poligono Sur.

El proyecto esta dividido en:

- `backend`: API con Django REST Framework.
- `frontend`: interfaz web con Angular.
- `PostgreSQL`: base de datos principal.
- `Redis` y `Celery`: tareas en segundo plano y generacion programada de partes.

## Requisitos

Para arrancarlo en local hace falta:

- Docker Desktop instalado y abierto.
- Git, si se clona desde GitHub.

No hace falta instalar Python, Node ni PostgreSQL en el ordenador si se usa Docker.

## Arrancar El Proyecto

Desde la carpeta raiz del proyecto:

```powershell
cd horarium
docker compose up -d --build
```

La primera vez puede tardar unos minutos porque descarga imagenes y compila el frontend.

Cuando termine, comprobar que los contenedores estan levantados:

```powershell
docker compose ps
```

Deberian aparecer servicios como `backend`, `frontend`, `db`, `redis`, `celery_worker` y `celery_beat`.

## Usuario De Prueba

Para una demo local se puede crear o resetear un usuario administrador con:

```powershell
docker compose exec backend python manage.py setup_demo_admin
```

Credenciales por defecto:

- Email: `admin@iespoligonosur.org`
- Contraseña: `admin1234`

Este usuario es solo para pruebas locales. Antes de un despliegue real habria que crear usuarios reales y cambiar contraseñas.

Si se quiere usar otra contraseña:

```powershell
docker compose exec backend python manage.py setup_demo_admin --password "otraPassword123"
```

## URLs Principales

- Aplicacion web: <http://localhost/>
- API backend: <http://localhost:8000/api/>
- Admin de Django: <http://localhost:8000/admin/>

Para entrar en la aplicacion web se usa el email y contraseña del usuario de prueba.

## Primer Uso Recomendado

1. Entrar en <http://localhost/> con el usuario de prueba.
2. Ir a `Importar Horario`.
3. Subir el fichero `backend/Datos_horarios.txt`.
4. Revisar que se crean profesores y entradas de horario.
5. Probar el buscador de horarios.
6. Crear una cuenta para algun profesor desde `Gestion de Usuarios`.
7. Registrar una ausencia.
8. Revisar las ausencias desde direccion.
9. Generar un parte PDF desde `Partes`.

## Parar El Proyecto

Para parar los contenedores:

```powershell
docker compose down
```

Para parar y borrar tambien los datos de la base de datos local:

```powershell
docker compose down -v
```

Ojo: `-v` elimina los datos guardados en PostgreSQL, incluyendo usuarios, horarios importados y partes.

## Problemas Comunes

Si el login falla despues de reconstruir el frontend, probar una recarga fuerte del navegador:

```text
Ctrl + F5
```

Tambien se puede abrir una ventana de incognito para evitar tokens antiguos guardados en `localStorage`.

Si el usuario de prueba no funciona, volver a ejecutar:

```powershell
docker compose exec backend python manage.py setup_demo_admin
```
