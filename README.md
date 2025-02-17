# Application

This is a simple Flask web application that returns "Hello, World!" when accessed.

### Running the Application

**Update environment variables**
```
cp .env.template .env
```

Add a password for postgres and edit any other variables you would like.

**Build & Run Services**
```
docker compose build
```

```
docker compose up -d
```

**Only Rebuild API**
```
docker compose up -d --no-deps --build api
```

**Send Test Request**
```
curl http://localhost:5000/health/shallow
```
