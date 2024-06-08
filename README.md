# Application
## Run Locally
**note**: You will still need to use docker for the database
### First time set up
```bash
sudo mkdir /var/log/outland-insights
sudo chmod 777 /var/log/outland-insights
```

### Run local Jar
```bash
mvn clean compile assembly:single

PG_HOST=localhost java -jar target/application.jar
```

## Run with Docker
By running with docker it will create a container for the api as well as the postgres database. This will also create networking between the two containers to allow them to communicate. 

### First Time

**Compile Jar with Dependencies**
```bash
mvn clean compile assembly:single
```

**Docker Compose**
```bash
docker compose up -d
```

### Rebuild Backend
**Compile Jar with Dependencies**
```bash
mvn clean compile assembly:single
```

**Rebuild backend API**
```bash
docker compose up -d --no-deps --build api
```

**Docker Compose**
```bash
docker compose up -d
```

### Only run database
```bash
// If previous running instances
docker compose down

// Only start database
docker compose up -d database
```

### Start/Stop Servers
**Docker Compose**
```bash
// Start
docker compose start

// Stop
docker compose stop
```

### Clear Database
**Docker Compose**
```bash
docker compose down -v
```

## Clean old docker images
```bash
docker image prune
```

## Database Migrations
### Platform Schema
```bash
mvn flyway:migrate@platform
```

### Security Schema
```bash
mvn flyway:migrate@security
```
