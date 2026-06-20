# Deployment

## Docker

```bash
docker-compose up --build
```

## Environment Variables

See `.env.example` for all configuration options.

## Redis

The service requires Redis for production use. Redis cluster is supported for high availability.

## Monitoring

Prometheus metrics are available at `/metrics`. Configure Prometheus to scrape this endpoint.
