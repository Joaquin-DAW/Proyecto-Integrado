# Manual de implantación y uso de Horarium

**Proyecto Integrado - Horarium**  
**Autor:** Joaquín Cabezas Berjillos  
**Centro:** IES Polígono Sur  
**Fecha:** junio de 2026

## 1. Introducción

Horarium es una aplicación web desarrollada para facilitar la gestión de horarios, ausencias del profesorado, guardias y partes diarios de ausencia en el IES Polígono Sur.

La aplicación permite importar el horario del centro desde un fichero de texto, registrar ausencias, consultar qué profesorado está de guardia, generar partes en PDF y enviarlos por correo electrónico al equipo directivo.

Este documento está planteado como manual de implantación y uso. Su objetivo es que una persona que parte de un equipo sin Docker instalado pueda desplegar el proyecto, configurarlo y empezar a trabajar con la aplicación.

## 2. Funcionalidades implementadas

Las funcionalidades principales de Horarium son:

- Inicio de sesión con usuarios y roles.
- Rol de profesorado.
- Rol de equipo directivo.
- Importación del horario desde un fichero `.txt`.
- Consulta de horarios por profesor, día, grupo, asignatura y aula.
- Panel diario para el equipo directivo.
- Registro de ausencias propias por parte del profesorado.
- Registro de ausencias de cualquier profesor por parte del equipo directivo.
- Campo de tareas asociado a la ausencia.
- Gestión de usuarios y creación de cuentas para el profesorado.
- Generación de partes de ausencia en PDF.
- Parte común del IES y partes por módulo.
- Envío de partes por correo electrónico.
- Tarea programada con Celery Beat para generar partes diarios.

## 3. Arquitectura general

Horarium está dividido en varios servicios que se ejecutan con Docker Compose:

- **Frontend:** aplicación Angular que muestra la interfaz web.
- **Backend:** API desarrollada con Django REST Framework.
- **PostgreSQL:** base de datos principal.
- **Redis:** cola de mensajes usada por Celery.
- **Celery worker:** ejecuta tareas en segundo plano.
- **Celery beat:** planifica tareas periódicas, como la generación diaria de partes.

La comunicación general es la siguiente:

1. El usuario entra en la aplicación web desde el navegador.
2. Angular realiza peticiones HTTP a la API de Django.
3. Django consulta y modifica los datos en PostgreSQL.
4. Para tareas programadas o en segundo plano se utiliza Celery con Redis.
5. Los PDFs generados se guardan como archivos del backend.
6. El envío de correos se realiza mediante SMTP si está configurado.

## 4. Requisitos previos

Para instalar Horarium en local se necesita:

- Un ordenador con Windows.
- Conexión a Internet para descargar Docker e imágenes.
- Docker Desktop instalado y abierto.
- Git instalado, si se va a clonar el repositorio desde GitHub.

No es necesario instalar Python, Node.js, PostgreSQL ni Redis manualmente, ya que Docker se encarga de ejecutar esos servicios en contenedores.

## 5. Instalación de Docker Desktop

Si el equipo no tiene Docker instalado:

1. Entrar en la documentación oficial de Docker Desktop para Windows:
   <https://docs.docker.com/desktop/setup/install/windows-install/>
2. Descargar Docker Desktop para Windows.
3. Ejecutar el instalador.
4. Mantener activada la opción de usar WSL 2 si el instalador la ofrece.
5. Reiniciar el equipo si Docker lo solicita.
6. Abrir Docker Desktop y esperar a que aparezca como iniciado.

Para comprobar que Docker funciona, abrir PowerShell y ejecutar:

```powershell
docker --version
docker compose version
```

Si ambos comandos responden con una versión, Docker está instalado correctamente.

**Captura recomendada:** Docker Desktop abierto y funcionando.

## 6. Obtener el proyecto desde GitHub

Abrir PowerShell en la carpeta donde se quiera guardar el proyecto y clonar el repositorio:

```powershell
git clone https://github.com/Joaquin-DAW/Proyecto-Integrado.git
cd Proyecto-Integrado
```

Si el repositorio contiene directamente la carpeta `horarium`, entrar en ella:

```powershell
cd horarium
```

Todos los comandos de arranque deben ejecutarse desde la carpeta donde está el archivo `docker-compose.yml`.

**Captura recomendada:** carpeta del proyecto con `docker-compose.yml`, `backend`, `frontend` y `README.md`.

## 7. Configuración del archivo .env

El proyecto usa un archivo `.env` para guardar variables de configuración. Este archivo no debe subirse a GitHub porque puede contener contraseñas.

Crear el `.env` a partir de la plantilla:

```powershell
copy .env.example .env
```

La configuración básica para desarrollo local es suficiente para arrancar la aplicación. Los valores más importantes son:

```env
SECRET_KEY=cambia-esta-clave-en-produccion-usa-una-larga-y-aleatoria
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=horarium
POSTGRES_USER=horarium
POSTGRES_PASSWORD=horarium123
POSTGRES_HOST=db
POSTGRES_PORT=5432

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

CORS_ALLOWED_ORIGINS=http://localhost,http://localhost:4200
FRONTEND_URL=http://localhost
```

## 8. Arrancar la aplicación

Desde la carpeta `horarium`, ejecutar:

```powershell
docker compose up -d --build
```

La primera vez puede tardar varios minutos porque Docker debe descargar imágenes y compilar el frontend.

Comprobar que los servicios están levantados:

```powershell
docker compose ps
```

Deben aparecer los siguientes servicios:

- `horarium_backend`
- `horarium_frontend`
- `horarium_db`
- `horarium_redis`
- `horarium_celery_worker`
- `horarium_celery_beat`

La aplicación web estará disponible en:

```text
http://localhost
```

La API estará disponible en:

```text
http://localhost:8000/api/
```

**Captura recomendada:** salida de `docker compose ps` con los contenedores levantados.

## 9. Crear usuario administrador de prueba

Para crear o resetear un usuario de equipo directivo de prueba:

```powershell
docker compose exec backend python manage.py setup_demo_admin
```

Credenciales por defecto:

- Email: `admin@iespoligonosur.org`
- Contraseña: `admin1234`

También se puede crear otro usuario de equipo directivo indicando correo y contraseña:

```powershell
docker compose exec backend python manage.py setup_demo_admin --email correo@ejemplo.com --password admin1234
```

Este usuario permite acceder a las funcionalidades de administración de la aplicación.

## 10. Primer acceso a la aplicación

Abrir el navegador y entrar en:

```text
http://localhost
```

Introducir el usuario de prueba:

- Email: `admin@iespoligonosur.org`
- Contraseña: `admin1234`

Al entrar como equipo directivo se muestra el panel diario de ausencias.

**Captura recomendada:** pantalla de login.

## 11. Importar horario

La primera acción recomendada es importar el horario del centro.

Pasos:

1. Entrar con usuario de equipo directivo.
2. Ir a `Importar Horario`.
3. Seleccionar el fichero `backend/Datos_horarios.txt`.
4. Pulsar el botón de importación.
5. Revisar el resumen de importación.

La importación crea profesores y entradas de horario a partir del fichero.

El fichero contiene datos como:

- asignatura;
- grupo o curso;
- aula;
- profesor;
- día de la semana;
- tramo horario.

**Captura recomendada:** pantalla de importación y resultado de la carga.

## 12. Panel diario del equipo directivo

El panel diario es la pantalla principal del equipo directivo.

Muestra:

- fecha seleccionada;
- total de ausencias;
- profesorado de guardia;
- guardias disponibles;
- guardias ausentes;
- módulo de cada guardia cuando se puede determinar;
- tareas asociadas a las ausencias.

Las guardias se clasifican según los datos del horario:

- `GUARDIA A` se considera módulo A.
- `GUARDIA B` se considera módulo B.
- `GUARDIA BIBLIOTECA` se considera módulo A.
- Si no hay información suficiente, se muestra como general.

Este panel permite que el equipo directivo vea rápidamente qué profesorado falta y qué profesorado puede cubrir las guardias.

**Captura recomendada:** panel diario con una ausencia y una tarea visible.

## 13. Buscar horario

La pantalla de búsqueda permite consultar el horario general del centro.

Filtros disponibles:

- profesor;
- día;
- grupo;
- asignatura;
- aula.

Ejemplos de uso:

- buscar todas las clases de un profesor;
- localizar una asignatura concreta;
- revisar qué ocurre en un aula;
- consultar el horario de un grupo.

**Captura recomendada:** búsqueda por asignatura y resultados.

## 14. Gestión de usuarios

La pantalla de usuarios permite al equipo directivo gestionar las cuentas del profesorado.

Desde esta pantalla se puede:

- ver el listado de profesores importados;
- crear una cuenta para un profesor;
- editar email;
- cambiar rol;
- eliminar cuentas cuando sea necesario.

El sistema diferencia entre:

- **Profesor:** persona que aparece en el horario importado.
- **Usuario:** cuenta que puede iniciar sesión en la aplicación.

Esto permite importar el horario completo aunque no todos los profesores tengan cuenta creada.

**Captura recomendada:** gestión de usuarios con profesores importados.

## 15. Registro de ausencias

Las ausencias se registran sobre una entrada concreta del horario. Esto permite saber exactamente qué clase, grupo, aula y tramo quedan afectados.

### 15.1. Ausencia registrada por profesorado

El profesorado puede:

1. Entrar con su cuenta.
2. Ir a `Mis ausencias`.
3. Seleccionar fecha.
4. Elegir los tramos afectados.
5. Añadir descripción.
6. Añadir tareas para la guardia.
7. Registrar la ausencia.

### 15.2. Ausencia registrada por equipo directivo

El equipo directivo puede registrar una ausencia para cualquier profesor:

1. Ir a `Gestión de ausencias`.
2. Seleccionar profesor.
3. Seleccionar fecha.
4. Seleccionar tramos.
5. Añadir descripción.
6. Añadir tareas.
7. Registrar ausencia.

El campo **tareas** sirve para indicar qué debe hacer el alumnado durante la guardia. No incluye adjuntos ni integración con Google Drive, para mantener el sistema simple y fácil de mantener.

**Captura recomendada:** formulario de ausencia con campo de tareas.

## 16. Partes de ausencia en PDF

Desde la pantalla `Partes`, el equipo directivo puede generar partes de ausencia.

Actualmente se puede generar:

- parte común del IES;
- parte de módulo A;
- parte de módulo B.

El flujo principal recomendado es el parte común del IES, ya que recoge la información general de ausencias y guardias sin depender de separar físicamente todos los casos por módulo.

El PDF incluye:

- fecha del parte;
- profesorado ausente;
- grupo;
- aula;
- estado de justificación;
- profesorado de guardia;
- tareas asociadas a las ausencias si existen.

Si se modifica una ausencia después de generar el PDF, conviene regenerar el parte para que incluya la información actualizada.

**Captura recomendada:** listado de partes y PDF generado.

## 17. Configuración de correo electrónico

El sistema puede enviar el parte por email a los miembros activos del equipo directivo.

Para activar correo real, configurar SMTP en `.env`.

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

En Gmail no se debe usar la contraseña normal de la cuenta. Se debe crear una contraseña de aplicación desde la cuenta de Google.

Después de cambiar `.env`, reiniciar backend y Celery:

```powershell
docker compose up -d --force-recreate backend celery_worker celery_beat
```

El parte se envía a los usuarios que cumplen estas condiciones:

- tienen rol `EQUIPO_DIRECTIVO`;
- están activos;
- tienen email configurado.

**Captura recomendada:** correo recibido con el parte adjunto.

## 18. Generación automática de partes

El proyecto incluye una tarea periódica configurada con Celery Beat.

Esta tarea genera el parte común del IES en días lectivos.

Para crear o actualizar la tarea:

```powershell
docker compose exec backend python manage.py setup_periodic_tasks
```

Servicios implicados:

- `celery_beat`: decide cuándo se ejecuta la tarea.
- `celery_worker`: ejecuta la tarea.
- `redis`: actúa como cola de mensajes.
- `backend`: contiene la lógica de generación de PDF.

## 19. Pruebas realizadas

Durante el desarrollo se han realizado pruebas manuales y automáticas.

### 19.1. Pruebas automáticas

Comando para ejecutar pruebas:

```powershell
docker compose exec backend python manage.py test
```

También se puede comprobar la configuración general de Django:

```powershell
docker compose exec backend python manage.py check
```

Las pruebas cubren, entre otros puntos:

- creación de ausencias;
- guardias de biblioteca asignadas a módulo A;
- envío de partes por email;
- generación del parte común;
- búsqueda de horarios por asignatura.

### 19.2. Pruebas manuales

Pruebas recomendadas:

1. Iniciar sesión como equipo directivo.
2. Importar horario.
3. Buscar horarios por profesor, grupo, asignatura y aula.
4. Crear cuenta para un profesor.
5. Registrar ausencia con tareas.
6. Comprobar que aparece en el panel diario.
7. Generar PDF.
8. Enviar PDF por email.
9. Entrar como profesor y revisar su horario.
10. Registrar ausencia propia desde el rol de profesor.

## 20. Problemas comunes

### Docker no encuentra el archivo docker-compose.yml

Este error suele aparecer si el comando se ejecuta desde una carpeta incorrecta:

```text
no configuration file provided: not found
```

Solución:

```powershell
cd C:\ruta\del\proyecto\horarium
docker compose up -d
```

### El login no funciona

Resetear el usuario demo:

```powershell
docker compose exec backend python manage.py setup_demo_admin
```

Si el navegador conserva un token antiguo, hacer una recarga fuerte:

```text
Ctrl + F5
```

También se puede probar en una ventana de incógnito.

### No aparece un cambio del frontend

Reconstruir frontend:

```powershell
docker compose build frontend
docker compose up -d frontend
```

### El correo no se envía

Comprobar:

- que `.env` está guardado;
- que el backend se ha reiniciado;
- que `EMAIL_BACKEND` usa SMTP;
- que Gmail usa contraseña de aplicación;
- que hay usuarios activos con rol de equipo directivo;
- que el correo no ha llegado a spam.

## 21. Parar o reiniciar el proyecto

Parar contenedores:

```powershell
docker compose down
```

Parar y borrar datos locales:

```powershell
docker compose down -v
```

El parámetro `-v` borra los volúmenes de Docker, incluyendo la base de datos local. Se perderán usuarios, horarios importados, ausencias y partes generados.

## 22. Despliegue en AWS Academy

Además del despliegue local con Docker Desktop, el proyecto puede desplegarse en AWS Academy usando una instancia EC2 con Docker Compose.

Para mantener el despliegue sencillo y adecuado a un entorno académico, la opción recomendada es:

- una instancia EC2;
- Docker y Docker Compose;
- PostgreSQL y Redis dentro de contenedores;
- frontend publicado en el puerto 80;
- backend accesible solo de forma interna desde Nginx;
- sin RDS, balanceador ni dominio en esta primera versión.

La guía detallada está en:

```text
docs/despliegue_aws_academy.md
```

Este despliegue permite enseñar la aplicación funcionando desde una IP pública de AWS sin añadir una arquitectura demasiado compleja.

## 23. Mejoras futuras

Algunas mejoras posibles para próximas versiones:

- Clonar horario de un profesor para gestionar sustituciones.
- Marcar profesores como activos o inactivos a nivel de plantilla.
- Indicar si una clase debe aparecer o no en el panel diario.
- Marcar clases como aula huésped.
- Añadir adjuntos a las tareas de ausencia.
- Mejorar el despliegue en un servidor externo con HTTPS.
- Añadir una pantalla específica de estadísticas o histórico.

## 24. Conclusión

Horarium cubre el flujo principal que necesita el centro para gestionar horarios, ausencias, guardias y partes diarios. La aplicación puede desplegarse localmente con Docker, importar los datos del horario real del centro y ofrecer al equipo directivo una visión diaria del profesorado ausente y disponible para guardias.

El sistema se ha mantenido sencillo para facilitar su uso, documentación y mantenimiento, priorizando las funcionalidades necesarias en el día a día del centro.
