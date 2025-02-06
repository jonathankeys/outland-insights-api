# Application

This is a simple Flask web application that returns "Hello, World!" when accessed.

### Running the Application

**Build & Run Services**
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
