# Application

Outland Insights is an application which handles the storage, retrieval, authentication, authorization, and 
analytics of GPS routes.

The goal is to provide a simple interface to interact with GPS routes to power use cases left up to the customer, 
whether building their own analytics views for the frontend or to just store and retrieve their data.

## Tenets
**Uncover Meaningful Insights**
We should always be looking to spot new trends across multiple routes and providing the data for new patterns and 
insights to be uncovered.

**Access is Secure and Focused**
Analytics are done at the owner and organization level, and accessible by those who have access to them. Privacy and 
proper data boundaries are built into the way we access the data.

**Flexible Data Access**
Users should be able to retrieve their data in widely supported formats, making it easy to use with different tools 
and libraries, and adapt to new types of analytics.

**Clear & Actionable Insights**
Data should be easy to interpret, so users can quickly understand what’s happening and put insights to good use.

### Building and Running the Application

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
