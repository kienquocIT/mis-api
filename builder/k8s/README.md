# Kubernetes Configuration for MIS Bflow

This directory contains Kubernetes configurations for deploying the MIS Bflow application.

## Directory Structure

```
k8s/
├── development/        # Development environment configs
│   ├── namespace.yaml
│   ├── mysql-deployment.yaml
│   ├── redis-deployment.yaml
│   ├── rabbitmq-deployment.yaml
│   ├── django-deployment.yaml
│   ├── celery-deployment.yaml
│   └── kustomization.yaml
├── staging/           # Staging environment (future)
└── production/        # Production environment (future)
```

## Quick Start

### Prerequisites

- Kubernetes cluster (local or cloud)
- kubectl configured
- Docker registry access

### Build Docker Image

```bash
# From the project root (sit/)
docker build -f builder/Dockerfile -t mis-django:dev-latest .

# Tag for your registry
docker tag mis-django:dev-latest your-registry/mis-django:dev-latest

# Push to registry
docker push your-registry/mis-django:dev-latest
```

### Deploy to Development

```bash
# Navigate to k8s directory
cd builder/k8s/development

# Apply all configurations
kubectl apply -k .

# Or apply individually
kubectl apply -f namespace.yaml
kubectl apply -f mysql-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f rabbitmq-deployment.yaml
kubectl apply -f django-deployment.yaml
kubectl apply -f celery-deployment.yaml
```

### Verify Deployment

```bash
# Check all resources
kubectl get all -n bflow-dev

# Check pod status
kubectl get pods -n bflow-dev

# Check services
kubectl get svc -n bflow-dev

# View logs
kubectl logs -n bflow-dev deployment/django-app
kubectl logs -n bflow-dev deployment/celery-worker
```

### Access the Application

```bash
# Port forward for local access
kubectl port-forward -n bflow-dev service/django-service 8000:80

# Access at http://localhost:8000
```

### Database Migration

```bash
# Run migrations manually if needed
kubectl exec -n bflow-dev deployment/django-app -- python manage.py migrate

# Create superuser
kubectl exec -it -n bflow-dev deployment/django-app -- python manage.py createsuperuser
```

## Configuration Management

### Environment Variables

Edit `django-config` ConfigMap in the deployment files or use kustomization overlays.

### Secrets Management

```bash
# Create secrets manually
kubectl create secret generic mysql-secret \
  --from-literal=mysql-root-password=your-password \
  --from-literal=mysql-password=your-password \
  -n bflow-dev

kubectl create secret generic rabbitmq-secret \
  --from-literal=rabbitmq-user=your-user \
  --from-literal=rabbitmq-password=your-password \
  -n bflow-dev
```

## Scaling

```bash
# Scale Django app
kubectl scale deployment/django-app --replicas=5 -n bflow-dev

# Scale Celery workers
kubectl scale deployment/celery-worker --replicas=3 -n bflow-dev
```

## Monitoring

```bash
# Check resource usage
kubectl top pods -n bflow-dev

# View events
kubectl get events -n bflow-dev --sort-by='.lastTimestamp'
```

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n bflow-dev
   kubectl logs <pod-name> -n bflow-dev
   ```

2. **Database connection issues**
   - Check MySQL pod is running
   - Verify secrets are created
   - Check service DNS resolution

3. **Image pull errors**
   - Verify image exists in registry
   - Check image pull secrets if using private registry

## Clean Up

```bash
# Delete all resources
kubectl delete -k .

# Or delete namespace (removes everything)
kubectl delete namespace bflow-dev
```

## Production Considerations

- Use external database (RDS, Cloud SQL)
- Configure proper resource limits
- Set up monitoring (Prometheus, Grafana)
- Configure autoscaling (HPA)
- Use proper secret management (Vault, Sealed Secrets)
- Set up ingress controller for external access
- Configure backup strategies

---

**Last Updated**: 2025-07-25  
**Maintained By**: DevOps Team