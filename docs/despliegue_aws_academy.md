# Despliegue de Horarium en AWS Academy

Esta guía explica un despliegue sencillo de Horarium en AWS Academy Learner Lab usando una instancia EC2 y Docker Compose.

La idea es mantener el despliegue simple y demostrable:

- una instancia EC2;
- Docker y Docker Compose;
- PostgreSQL dentro de Docker;
- Redis dentro de Docker;
- frontend Angular servido por Nginx en el puerto 80;
- backend Django con Gunicorn dentro de Docker;
- Celery worker y Celery beat dentro de Docker.

No se usan RDS, balanceadores, dominios ni HTTPS en esta primera versión para evitar complejidad y consumo innecesario del presupuesto del laboratorio.

## 1. Preparación en AWS Academy

1. Entrar en AWS Academy Learner Lab.
2. Pulsar `Comenzar` o `Start Lab`.
3. Esperar a que el laboratorio esté iniciado.
4. Abrir la consola de AWS desde el botón del laboratorio.
5. Ir al servicio `EC2`.

## 2. Crear instancia EC2

Configuración recomendada:

- **AMI:** Ubuntu Server LTS.
- **Tipo de instancia:** `t3.small` o `t3.medium` si el laboratorio lo permite.
- **Almacenamiento:** 20 GB como mínimo.
- **Key pair:** crear o usar una clave existente para conectarse por SSH.

Una instancia `t2.micro` o `t3.micro` puede quedarse corta al compilar el frontend y levantar todos los contenedores.

## 3. Security Group

Reglas de entrada recomendadas:

| Tipo | Puerto | Origen | Uso |
| --- | --- | --- | --- |
| SSH | 22 | Mi IP | Conexión al servidor |
| HTTP | 80 | 0.0.0.0/0 | Acceso a Horarium desde navegador |

No abrir estos puertos al exterior:

- `5432` PostgreSQL.
- `6379` Redis.
- `8000` Backend Django.

El frontend de Nginx recibe las peticiones públicas en el puerto 80 y redirige internamente `/api/` hacia el backend.

## 4. Conectarse por SSH

Desde PowerShell, usando la clave descargada al crear la instancia:

```powershell
ssh -i "ruta\a\tu-clave.pem" ubuntu@IP_PUBLICA_EC2
```

En la consola de EC2 también se puede usar el botón `Connect` para copiar el comando exacto.

## 5. Instalar Docker en la instancia

Ejecutar en la EC2:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME}) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Cerrar la sesión SSH y volver a entrar para que el grupo `docker` se aplique.

Comprobar:

```bash
docker --version
docker compose version
```

## 6. Clonar el repositorio

En la EC2:

```bash
git clone https://github.com/Joaquin-DAW/Proyecto-Integrado.git
cd Proyecto-Integrado
```

El archivo `docker-compose.prod.yml` debe estar en esta carpeta. Si el repositorio tuviera una carpeta interna `horarium`, entrar en ella antes de continuar.

## 7. Crear .env para AWS

Copiar la plantilla:

```bash
cp .env.aws.example .env
```

Editar:

```bash
nano .env
```

Valores importantes:

```env
DEBUG=False
ALLOWED_HOSTS=IP_PUBLICA_EC2,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://IP_PUBLICA_EC2
FRONTEND_URL=http://IP_PUBLICA_EC2
POSTGRES_PASSWORD=una-password-segura
```

Generar una clave secreta para Django:

```bash
openssl rand -base64 48
```

Copiar el resultado en:

```env
SECRET_KEY=resultado-generado
```

Si se quiere probar envío real de correos, configurar también SMTP. Si no, se puede dejar el backend de consola.

## 8. Levantar Horarium en AWS

Ejecutar:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Comprobar contenedores:

```bash
docker compose -f docker-compose.prod.yml ps
```

Ver logs del backend si algo falla:

```bash
docker compose -f docker-compose.prod.yml logs -f backend
```

## 9. Crear usuario de prueba

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py setup_demo_admin
```

Credenciales:

- Email: `admin@iespoligonosur.org`
- Contraseña: `admin1234`

## 10. Acceder a la aplicación

Abrir en el navegador:

```text
http://IP_PUBLICA_EC2
```

Desde ahí se puede:

1. iniciar sesión;
2. importar el horario;
3. registrar ausencias;
4. generar partes;
5. probar el panel diario.

## 11. Actualizar cambios

Si se suben cambios nuevos a GitHub:

```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## 12. Parar la aplicación

Para parar contenedores sin borrar datos:

```bash
docker compose -f docker-compose.prod.yml down
```

No usar `-v` salvo que se quiera borrar la base de datos y los PDFs generados.

## 13. Recomendaciones para AWS Academy

- No crear RDS, Load Balancer ni NAT Gateway para esta demo.
- Parar la instancia cuando no se esté usando.
- Vigilar el presupuesto del laboratorio.
- No abrir PostgreSQL ni Redis a Internet.
- Guardar la clave `.pem` en un sitio seguro.
- No subir `.env` al repositorio.

## 14. Fuentes oficiales

- EC2: <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html>
- Security Groups: <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html>
- Docker en Ubuntu: <https://docs.docker.com/engine/install/ubuntu/>
