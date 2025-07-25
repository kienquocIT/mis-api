# Deployment Guide - Bflow Workflow Management System
**Version:** 1.0  
**Date:** 2025-07-25  
**Author:** DevOps Engineer  
**Status:** Draft

## 1. Overview

### 1.1 Purpose
Tài liệu này cung cấp hướng dẫn chi tiết để deploy Bflow Workflow Management System lên các môi trường khác nhau, từ development đến production, sử dụng các best practices của DevOps.

### 1.2 Deployment Architecture Overview

```mermaid
graph TB
    subgraph "Developer Machine"
        Dev[Local Development]
        Git[Git Repository]
    end
    
    subgraph "CI/CD Pipeline"
        GitLab[GitLab CI/CD]
        Build[Build Stage]
        Test[Test Stage]
        Package[Package Stage]
        Deploy[Deploy Stage]
    end
    
    subgraph "Container Registry"
        Registry[Docker Registry]
        Images[Docker Images]
    end
    
    subgraph "Environments"
        DevEnv[Development]
        TestEnv[Testing]
        StagingEnv[Staging]
        ProdEnv[Production]
    end
    
    subgraph "Infrastructure"
        K8s[Kubernetes Cluster]
        MySQL[MySQL Cluster]
        Redis[Redis Cluster]
        RabbitMQ[RabbitMQ Cluster]
        S3[Object Storage]
    end
    
    Dev --> Git
    Git --> GitLab
    GitLab --> Build
    Build --> Test
    Test --> Package
    Package --> Registry
    Registry --> Deploy
    Deploy --> DevEnv
    Deploy --> TestEnv
    Deploy --> StagingEnv
    Deploy --> ProdEnv
    
    DevEnv --> K8s
    TestEnv --> K8s
    StagingEnv --> K8s
    ProdEnv --> K8s
    
    K8s --> MySQL
    K8s --> Redis
    K8s --> RabbitMQ
    K8s --> S3
```

### 1.3 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Container Runtime** | Docker | 24.x | Application containerization |
| **Orchestration** | Kubernetes | 1.28.x | Container orchestration |
| **CI/CD** | GitLab CI | Latest | Continuous Integration/Deployment |
| **Service Mesh** | Istio | 1.19.x | Microservices communication |
| **Monitoring** | Prometheus + Grafana | Latest | Metrics and monitoring |
| **Logging** | ELK Stack | 8.x | Centralized logging |
| **Tracing** | Jaeger | Latest | Distributed tracing |
| **Secrets Management** | HashiCorp Vault | 1.15.x | Secrets and certificates |

## 2. Prerequisites

### 2.1 Infrastructure Requirements

#### Development Environment
```yaml
resources:
  cpu: 2 cores
  memory: 4GB RAM
  storage: 20GB SSD
  
services:
  - Docker Desktop
  - Python 3.11+
  - Node.js 18+
  - Git
```

#### Production Environment
```yaml
kubernetes_cluster:
  nodes:
    master: 3 (High Availability)
    worker: 5 minimum
  
  node_specs:
    master:
      cpu: 4 cores
      memory: 16GB
      storage: 100GB SSD
    worker:
      cpu: 8 cores
      memory: 32GB
      storage: 200GB SSD

databases:
  mysql:
    version: 8.0
    nodes: 3 (Primary + 2 Replicas)
    storage: 500GB SSD per node
    
  redis:
    version: 7.x
    mode: Cluster (6 nodes)
    memory: 16GB per node
    
  rabbitmq:
    version: 3.12
    nodes: 3 (Cluster)
    storage: 100GB per node

storage:
  object_storage:
    provider: MinIO/S3
    capacity: 1TB minimum
    redundancy: 3x replication
```

### 2.2 Software Requirements

```bash
# Required CLI tools
- kubectl v1.28+
- helm v3.13+
- docker v24+
- docker-compose v2.23+
- git v2.40+
- python v3.11+
- terraform v1.6+ (for IaC)
- ansible v2.16+ (for configuration management)
```

### 2.3 Access Requirements

- Kubernetes cluster admin access
- Docker registry push access
- Database admin credentials
- SSL certificates for domains
- Cloud provider credentials (if applicable)

## 3. Environment Configuration

### 3.1 Environment Variables

```bash
# .env.example
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=api.bflow.com,*.bflow.local

# Database Configuration
DB_ENGINE=django.db.backends.mysql
DB_HOST=mysql-primary.bflow.svc.cluster.local
DB_PORT=3306
DB_NAME=bflow_production
DB_USER=bflow_user
DB_PASSWORD=secure-password-here
DB_OPTIONS_CHARSET=utf8mb4

# Redis Configuration
REDIS_HOST=redis-cluster.bflow.svc.cluster.local
REDIS_PORT=6379
REDIS_PASSWORD=redis-password-here
REDIS_DB=0

# RabbitMQ Configuration
RABBITMQ_HOST=rabbitmq-cluster.bflow.svc.cluster.local
RABBITMQ_PORT=5672
RABBITMQ_USER=bflow
RABBITMQ_PASSWORD=rabbitmq-password-here
RABBITMQ_VHOST=/bflow

# Celery Configuration
CELERY_BROKER_URL=amqp://bflow:password@rabbitmq-cluster:5672/bflow
CELERY_RESULT_BACKEND=redis://:password@redis-cluster:6379/1

# Storage Configuration
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
AWS_ACCESS_KEY_ID=minio-access-key
AWS_SECRET_ACCESS_KEY=minio-secret-key
AWS_STORAGE_BUCKET_NAME=bflow-media
AWS_S3_ENDPOINT_URL=http://minio.bflow.svc.cluster.local:9000

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=sendgrid-api-key

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Monitoring
PROMETHEUS_EXPORT_MIGRATIONS=False
OPENTELEMETRY_ENDPOINT=http://jaeger-collector:14268/api/traces

# Feature Flags
ENABLE_WORKFLOW_VERSIONING=True
ENABLE_AI_FEATURES=False
ENABLE_ADVANCED_ANALYTICS=True
```

### 3.2 Environment-Specific Configurations

#### Development
```yaml
# config/environments/development.yaml
environment: development
debug: true
log_level: DEBUG
replicas:
  api: 1
  worker: 1
  scheduler: 1
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### Staging
```yaml
# config/environments/staging.yaml
environment: staging
debug: false
log_level: INFO
replicas:
  api: 2
  worker: 2
  scheduler: 1
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
autoscaling:
  enabled: true
  min_replicas: 2
  max_replicas: 5
  target_cpu: 70
```

#### Production
```yaml
# config/environments/production.yaml
environment: production
debug: false
log_level: WARNING
replicas:
  api: 3
  worker: 5
  scheduler: 2
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
autoscaling:
  enabled: true
  min_replicas: 3
  max_replicas: 10
  target_cpu: 60
  target_memory: 70
pod_disruption_budget:
  min_available: 2
```

## 4. Docker Configuration

### 4.1 Dockerfile

```dockerfile
# Dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmariadb-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libmariadb3 \
    libxml2 \
    libxslt1.1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 bflow && \
    chown -R bflow:bflow /app

USER bflow

# Environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=misapi.settings

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--worker-class", "gthread", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "misapi.wsgi:application"]
```

### 4.2 Docker Compose (Development)

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    container_name: bflow-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: bflow_dev
      MYSQL_USER: bflow
      MYSQL_PASSWORD: bflowpass
    ports:
      - "3307:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: bflow-redis
    command: redis-server --requirepass redispass
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  rabbitmq:
    image: rabbitmq:3.12-management
    container_name: bflow-rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: bflow
      RABBITMQ_DEFAULT_PASS: rabbitmqpass
      RABBITMQ_DEFAULT_VHOST: /bflow
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: bflow-minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: bflow-api
    env_file:
      - .env.development
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    command: python manage.py runserver 0.0.0.0:8000

  celery:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: bflow-celery
    env_file:
      - .env.development
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
      - rabbitmq
    command: celery -A misapi worker --loglevel=info

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: bflow-celery-beat
    env_file:
      - .env.development
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
      - rabbitmq
    command: celery -A misapi beat --loglevel=info

  flower:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: bflow-flower
    env_file:
      - .env.development
    ports:
      - "5555:5555"
    depends_on:
      - redis
      - rabbitmq
    command: celery -A misapi flower

volumes:
  mysql_data:
  redis_data:
  rabbitmq_data:
  minio_data:
```

## 5. Kubernetes Deployment

### 5.1 Namespace and ConfigMap

```yaml
# k8s/00-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bflow
  labels:
    name: bflow
    environment: production

---
# k8s/01-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: bflow-config
  namespace: bflow
data:
  DJANGO_SETTINGS_MODULE: "misapi.settings"
  DJANGO_ALLOWED_HOSTS: "api.bflow.com,*.bflow.local"
  DB_ENGINE: "django.db.backends.mysql"
  DB_HOST: "mysql-primary.bflow.svc.cluster.local"
  DB_PORT: "3306"
  DB_NAME: "bflow_production"
  REDIS_HOST: "redis-cluster.bflow.svc.cluster.local"
  REDIS_PORT: "6379"
  RABBITMQ_HOST: "rabbitmq-cluster.bflow.svc.cluster.local"
  RABBITMQ_PORT: "5672"
  RABBITMQ_VHOST: "/bflow"
  AWS_STORAGE_BUCKET_NAME: "bflow-media"
  AWS_S3_ENDPOINT_URL: "http://minio.bflow.svc.cluster.local:9000"
  PROMETHEUS_EXPORT_MIGRATIONS: "False"
  OPENTELEMETRY_ENDPOINT: "http://jaeger-collector:14268/api/traces"
```

### 5.2 Secrets Management

```yaml
# k8s/02-secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: bflow-secrets
  namespace: bflow
type: Opaque
stringData:
  DJANGO_SECRET_KEY: "your-production-secret-key"
  DB_USER: "bflow_user"
  DB_PASSWORD: "secure-database-password"
  REDIS_PASSWORD: "secure-redis-password"
  RABBITMQ_USER: "bflow"
  RABBITMQ_PASSWORD: "secure-rabbitmq-password"
  AWS_ACCESS_KEY_ID: "minio-access-key"
  AWS_SECRET_ACCESS_KEY: "minio-secret-key"
  EMAIL_HOST_PASSWORD: "sendgrid-api-key"

---
# External Secrets Operator (Recommended for Production)
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: bflow
spec:
  provider:
    vault:
      server: "https://vault.bflow.com:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "bflow"
          serviceAccountRef:
            name: "bflow-api"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: bflow-secrets
  namespace: bflow
spec:
  refreshInterval: 15m
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: bflow-secrets
    creationPolicy: Owner
  dataFrom:
  - extract:
      key: /bflow/production
```

### 5.3 API Deployment

```yaml
# k8s/10-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bflow-api
  namespace: bflow
  labels:
    app: bflow-api
    component: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: bflow-api
  template:
    metadata:
      labels:
        app: bflow-api
        component: backend
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: bflow-api
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: api
        image: registry.gitlab.com/bflow/api:v1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
          protocol: TCP
        envFrom:
        - configMapRef:
            name: bflow-config
        - secretRef:
            name: bflow-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        volumeMounts:
        - name: static-files
          mountPath: /app/static
        - name: media-files
          mountPath: /app/media
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
      initContainers:
      - name: migrate
        image: registry.gitlab.com/bflow/api:v1.0.0
        command: ['python', 'manage.py', 'migrate', '--noinput']
        envFrom:
        - configMapRef:
            name: bflow-config
        - secretRef:
            name: bflow-secrets
      - name: collectstatic
        image: registry.gitlab.com/bflow/api:v1.0.0
        command: ['python', 'manage.py', 'collectstatic', '--noinput']
        volumeMounts:
        - name: static-files
          mountPath: /app/static
      volumes:
      - name: static-files
        persistentVolumeClaim:
          claimName: bflow-static-pvc
      - name: media-files
        persistentVolumeClaim:
          claimName: bflow-media-pvc
      imagePullSecrets:
      - name: gitlab-registry

---
# k8s/11-api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: bflow-api
  namespace: bflow
  labels:
    app: bflow-api
spec:
  type: ClusterIP
  selector:
    app: bflow-api
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
    name: http

---
# k8s/12-api-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bflow-api-hpa
  namespace: bflow
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bflow-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 15
      selectPolicy: Max

---
# k8s/13-api-pdb.yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: bflow-api-pdb
  namespace: bflow
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: bflow-api
```

### 5.4 Celery Workers Deployment

```yaml
# k8s/20-celery-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bflow-celery
  namespace: bflow
  labels:
    app: bflow-celery
    component: worker
spec:
  replicas: 5
  selector:
    matchLabels:
      app: bflow-celery
  template:
    metadata:
      labels:
        app: bflow-celery
        component: worker
    spec:
      serviceAccountName: bflow-celery
      containers:
      - name: celery
        image: registry.gitlab.com/bflow/api:v1.0.0
        imagePullPolicy: Always
        command: ["celery", "-A", "misapi", "worker", "--loglevel=info", "--concurrency=4"]
        envFrom:
        - configMapRef:
            name: bflow-config
        - secretRef:
            name: bflow-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - celery
            - -A
            - misapi
            - inspect
            - ping
          initialDelaySeconds: 30
          periodSeconds: 60
      imagePullSecrets:
      - name: gitlab-registry

---
# k8s/21-celery-beat-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bflow-celery-beat
  namespace: bflow
  labels:
    app: bflow-celery-beat
    component: scheduler
spec:
  replicas: 1  # Only one beat instance
  selector:
    matchLabels:
      app: bflow-celery-beat
  template:
    metadata:
      labels:
        app: bflow-celery-beat
        component: scheduler
    spec:
      serviceAccountName: bflow-celery
      containers:
      - name: celery-beat
        image: registry.gitlab.com/bflow/api:v1.0.0
        imagePullPolicy: Always
        command: ["celery", "-A", "misapi", "beat", "--loglevel=info"]
        envFrom:
        - configMapRef:
            name: bflow-config
        - secretRef:
            name: bflow-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "250m"
        volumeMounts:
        - name: celery-beat-schedule
          mountPath: /app/celerybeat-schedule
      volumes:
      - name: celery-beat-schedule
        persistentVolumeClaim:
          claimName: celery-beat-pvc
      imagePullSecrets:
      - name: gitlab-registry
```

### 5.5 Ingress Configuration

```yaml
# k8s/30-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: bflow-ingress
  namespace: bflow
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://app.bflow.com"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization"
spec:
  tls:
  - hosts:
    - api.bflow.com
    secretName: bflow-tls
  rules:
  - host: api.bflow.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: bflow-api
            port:
              number: 80

---
# k8s/31-certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: bflow-tls
  namespace: bflow
spec:
  secretName: bflow-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  commonName: api.bflow.com
  dnsNames:
  - api.bflow.com
  - www.api.bflow.com
```

### 5.6 Persistent Volumes

```yaml
# k8s/40-persistent-volumes.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: bflow-static-pvc
  namespace: bflow
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: efs-sc  # AWS EFS or similar
  resources:
    requests:
      storage: 10Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: bflow-media-pvc
  namespace: bflow
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: efs-sc
  resources:
    requests:
      storage: 100Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: celery-beat-pvc
  namespace: bflow
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: gp2
  resources:
    requests:
      storage: 1Gi
```

## 6. Database Deployment

### 6.1 MySQL Cluster with Operator

```yaml
# k8s/mysql/mysql-cluster.yaml
apiVersion: mysql.oracle.com/v2
kind: InnoDBCluster
metadata:
  name: mysql-cluster
  namespace: bflow
spec:
  secretName: mysql-root-secret
  tlsUseSelfSigned: true
  instances: 3
  router:
    instances: 2
  version: 8.0.35
  
  datadirVolumeClaimTemplate:
    accessModes:
    - ReadWriteOnce
    resources:
      requests:
        storage: 500Gi
    storageClassName: fast-ssd
  
  podSpec:
    containers:
    - name: mysql
      resources:
        requests:
          memory: "4Gi"
          cpu: "2"
        limits:
          memory: "8Gi"
          cpu: "4"
  
  backup:
    profiles:
    - name: daily-backup
      dumpInstance:
        storage:
          s3:
            bucketName: bflow-mysql-backups
            endpoint: s3.amazonaws.com
            profile: default
            prefix: /mysql-backups
      schedules:
      - name: daily
        schedule: "0 2 * * *"
        backupProfileName: daily-backup
        enabled: true
```

### 6.2 Redis Cluster

```yaml
# k8s/redis/redis-cluster.yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: redis-cluster
  namespace: bflow
spec:
  clusterSize: 6
  kubernetesConfig:
    image: redis:7-alpine
    resources:
      requests:
        cpu: 250m
        memory: 512Mi
      limits:
        cpu: 500m
        memory: 1Gi
  redisExporter:
    enabled: true
    image: oliver006/redis_exporter:latest
  storage:
    volumeClaimTemplate:
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 10Gi
        storageClassName: fast-ssd
  securityContext:
    runAsUser: 1000
    fsGroup: 1000
  podSecurityPolicy:
    enabled: true
```

### 6.3 RabbitMQ Cluster

```yaml
# k8s/rabbitmq/rabbitmq-cluster.yaml
apiVersion: rabbitmq.com/v1beta1
kind: RabbitmqCluster
metadata:
  name: rabbitmq-cluster
  namespace: bflow
spec:
  replicas: 3
  image: rabbitmq:3.12-management
  service:
    type: ClusterIP
  persistence:
    storageClassName: fast-ssd
    storage: 100Gi
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1
      memory: 2Gi
  rabbitmq:
    additionalConfig: |
      cluster_partition_handling = pause_minority
      vm_memory_high_watermark_paging_ratio = 0.99
      disk_free_limit.relative = 1.5
  override:
    statefulSet:
      spec:
        template:
          spec:
            containers:
            - name: rabbitmq
              env:
              - name: RABBITMQ_DEFAULT_USER
                valueFrom:
                  secretKeyRef:
                    name: bflow-secrets
                    key: RABBITMQ_USER
              - name: RABBITMQ_DEFAULT_PASS
                valueFrom:
                  secretKeyRef:
                    name: bflow-secrets
                    key: RABBITMQ_PASSWORD
```

## 7. Monitoring Stack

### 7.1 Prometheus Configuration

```yaml
# k8s/monitoring/prometheus-values.yaml
prometheus:
  prometheusSpec:
    retention: 30d
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: fast-ssd
          resources:
            requests:
              storage: 100Gi
    
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    
    additionalScrapeConfigs:
    - job_name: 'bflow-api'
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - bflow
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__

grafana:
  adminPassword: secure-password-here
  persistence:
    enabled: true
    storageClassName: fast-ssd
    size: 10Gi
  
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
      - name: 'bflow'
        orgId: 1
        folder: 'Bflow'
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards/bflow
  
  dashboards:
    bflow:
      bflow-overview:
        url: https://raw.githubusercontent.com/bflow/dashboards/main/overview.json
      bflow-api:
        url: https://raw.githubusercontent.com/bflow/dashboards/main/api.json
      bflow-celery:
        url: https://raw.githubusercontent.com/bflow/dashboards/main/celery.json

alertmanager:
  alertmanagerSpec:
    storage:
      volumeClaimTemplate:
        spec:
          storageClassName: fast-ssd
          resources:
            requests:
              storage: 10Gi
```

### 7.2 Application Metrics

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
workflow_executions = Counter(
    'bflow_workflow_executions_total',
    'Total number of workflow executions',
    ['workflow_name', 'status']
)

workflow_duration = Histogram(
    'bflow_workflow_duration_seconds',
    'Workflow execution duration in seconds',
    ['workflow_name'],
    buckets=[10, 30, 60, 120, 300, 600, 1800, 3600]
)

active_tasks = Gauge(
    'bflow_active_tasks',
    'Number of active tasks',
    ['task_type', 'priority']
)

api_request_duration = Histogram(
    'bflow_api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint', 'status'],
    buckets=[0.1, 0.5, 1, 2, 5, 10]
)

# Middleware for automatic API metrics
class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        api_request_duration.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).observe(duration)
        
        return response
```

## 8. CI/CD Pipeline

### 8.1 GitLab CI Configuration

```yaml
# .gitlab-ci.yml
variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  REGISTRY: registry.gitlab.com
  IMAGE_NAME: $REGISTRY/$CI_PROJECT_PATH
  KUBECTL_VERSION: 1.28.4
  HELM_VERSION: 3.13.2

stages:
  - build
  - test
  - security
  - package
  - deploy

# Build stage
build:
  stage: build
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
  only:
    - branches
    - tags

# Test stage
test:unit:
  stage: test
  image: python:3.11
  services:
    - mysql:8.0
    - redis:7-alpine
  variables:
    MYSQL_ROOT_PASSWORD: test
    MYSQL_DATABASE: bflow_test
    DB_HOST: mysql
    REDIS_HOST: redis
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-test.txt
  script:
    - pytest tests/unit --cov=apps --cov-report=xml --junitxml=junit.xml
    - coverage report --fail-under=80
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  coverage: '/TOTAL.+?(\d+\%)/'

test:integration:
  stage: test
  image: python:3.11
  services:
    - mysql:8.0
    - redis:7-alpine
    - rabbitmq:3.12
  script:
    - pytest tests/integration -v
  only:
    - merge_requests
    - develop
    - master

# Security scanning
security:sast:
  stage: security
  image: python:3.11
  script:
    - pip install safety bandit
    - safety check --json > safety-report.json || true
    - bandit -r apps/ -f json -o bandit-report.json || true
  artifacts:
    reports:
      sast: 
        - safety-report.json
        - bandit-report.json
  only:
    - merge_requests
    - develop
    - master

security:container:
  stage: security
  image: aquasec/trivy:latest
  script:
    - trivy image --no-progress --format json --output trivy-report.json $IMAGE_NAME:$CI_COMMIT_SHA
  artifacts:
    reports:
      container_scanning: trivy-report.json
  dependencies:
    - build

# Package stage
package:tag:
  stage: package
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker pull $IMAGE_NAME:$CI_COMMIT_SHA
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHA $IMAGE_NAME:$CI_COMMIT_REF_NAME
    - docker push $IMAGE_NAME:$CI_COMMIT_REF_NAME
  only:
    - tags

package:latest:
  stage: package
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker pull $IMAGE_NAME:$CI_COMMIT_SHA
    - docker tag $IMAGE_NAME:$CI_COMMIT_SHA $IMAGE_NAME:latest
    - docker push $IMAGE_NAME:latest
  only:
    - master

# Deploy stages
.deploy:
  image: bitnami/kubectl:$KUBECTL_VERSION
  before_script:
    - echo $KUBE_CONFIG | base64 -d > ~/.kube/config
    - kubectl version --client

deploy:dev:
  extends: .deploy
  stage: deploy
  environment:
    name: development
    url: https://dev-api.bflow.com
  script:
    - kubectl set image deployment/bflow-api api=$IMAGE_NAME:$CI_COMMIT_SHA -n bflow-dev
    - kubectl rollout status deployment/bflow-api -n bflow-dev
  only:
    - develop

deploy:staging:
  extends: .deploy
  stage: deploy
  environment:
    name: staging
    url: https://staging-api.bflow.com
  script:
    - kubectl set image deployment/bflow-api api=$IMAGE_NAME:$CI_COMMIT_SHA -n bflow-staging
    - kubectl rollout status deployment/bflow-api -n bflow-staging
  only:
    - master

deploy:production:
  extends: .deploy
  stage: deploy
  environment:
    name: production
    url: https://api.bflow.com
  script:
    - kubectl set image deployment/bflow-api api=$IMAGE_NAME:$CI_COMMIT_REF_NAME -n bflow
    - kubectl set image deployment/bflow-celery celery=$IMAGE_NAME:$CI_COMMIT_REF_NAME -n bflow
    - kubectl set image deployment/bflow-celery-beat celery-beat=$IMAGE_NAME:$CI_COMMIT_REF_NAME -n bflow
    - kubectl rollout status deployment/bflow-api -n bflow
    - kubectl rollout status deployment/bflow-celery -n bflow
  when: manual
  only:
    - tags
```

## 9. Deployment Procedures

### 9.1 Initial Deployment

```bash
#!/bin/bash
# scripts/initial-deployment.sh

set -e

ENVIRONMENT=$1
NAMESPACE="bflow-${ENVIRONMENT}"

echo "Starting initial deployment for environment: ${ENVIRONMENT}"

# Create namespace
kubectl create namespace ${NAMESPACE} || true

# Install cert-manager if not exists
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for cert-manager
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager -n cert-manager

# Apply configurations
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets.yaml

# Deploy databases
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add mysql-operator https://mysql.github.io/mysql-operator/
helm repo add rabbitmq https://charts.bitnami.com/bitnami
helm repo update

# Install MySQL
helm install mysql-cluster mysql-operator/mysql-innodbcluster \
  -f k8s/mysql/values.yaml \
  -n ${NAMESPACE}

# Install Redis
helm install redis-cluster bitnami/redis \
  -f k8s/redis/values.yaml \
  -n ${NAMESPACE}

# Install RabbitMQ
helm install rabbitmq-cluster bitnami/rabbitmq \
  -f k8s/rabbitmq/values.yaml \
  -n ${NAMESPACE}

# Wait for databases
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=mysql -n ${NAMESPACE} --timeout=600s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis -n ${NAMESPACE} --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=rabbitmq -n ${NAMESPACE} --timeout=300s

# Deploy application
kubectl apply -f k8s/10-api-deployment.yaml
kubectl apply -f k8s/11-api-service.yaml
kubectl apply -f k8s/12-api-hpa.yaml
kubectl apply -f k8s/13-api-pdb.yaml
kubectl apply -f k8s/20-celery-deployment.yaml
kubectl apply -f k8s/21-celery-beat-deployment.yaml

# Setup ingress
kubectl apply -f k8s/30-ingress.yaml
kubectl apply -f k8s/31-certificate.yaml

# Deploy monitoring
helm install prometheus prometheus-community/kube-prometheus-stack \
  -f k8s/monitoring/prometheus-values.yaml \
  -n monitoring --create-namespace

echo "Initial deployment completed!"
```

### 9.2 Rolling Update Procedure

```bash
#!/bin/bash
# scripts/rolling-update.sh

set -e

IMAGE_TAG=$1
NAMESPACE=$2

echo "Starting rolling update to version: ${IMAGE_TAG}"

# Update deployments
kubectl set image deployment/bflow-api api=registry.gitlab.com/bflow/api:${IMAGE_TAG} -n ${NAMESPACE}
kubectl set image deployment/bflow-celery celery=registry.gitlab.com/bflow/api:${IMAGE_TAG} -n ${NAMESPACE}
kubectl set image deployment/bflow-celery-beat celery-beat=registry.gitlab.com/bflow/api:${IMAGE_TAG} -n ${NAMESPACE}

# Wait for rollout
kubectl rollout status deployment/bflow-api -n ${NAMESPACE}
kubectl rollout status deployment/bflow-celery -n ${NAMESPACE}
kubectl rollout status deployment/bflow-celery-beat -n ${NAMESPACE}

# Run post-deployment checks
./scripts/health-check.sh ${NAMESPACE}

echo "Rolling update completed successfully!"
```

### 9.3 Rollback Procedure

```bash
#!/bin/bash
# scripts/rollback.sh

set -e

NAMESPACE=$1

echo "Starting rollback procedure..."

# Rollback deployments
kubectl rollout undo deployment/bflow-api -n ${NAMESPACE}
kubectl rollout undo deployment/bflow-celery -n ${NAMESPACE}
kubectl rollout undo deployment/bflow-celery-beat -n ${NAMESPACE}

# Wait for rollback
kubectl rollout status deployment/bflow-api -n ${NAMESPACE}
kubectl rollout status deployment/bflow-celery -n ${NAMESPACE}
kubectl rollout status deployment/bflow-celery-beat -n ${NAMESPACE}

# Verify health
./scripts/health-check.sh ${NAMESPACE}

echo "Rollback completed!"
```

### 9.4 Health Check Script

```bash
#!/bin/bash
# scripts/health-check.sh

set -e

NAMESPACE=$1
API_URL="https://api.bflow.com"

echo "Running health checks..."

# Check pod status
echo "Checking pod status..."
kubectl get pods -n ${NAMESPACE} | grep -E "(bflow-api|bflow-celery|mysql|redis|rabbitmq)"

# Check API health
echo "Checking API health..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/health/)
if [ ${HTTP_CODE} -eq 200 ]; then
    echo "✓ API health check passed"
else
    echo "✗ API health check failed with code: ${HTTP_CODE}"
    exit 1
fi

# Check database connectivity
echo "Checking database connectivity..."
kubectl exec -it deployment/bflow-api -n ${NAMESPACE} -- python manage.py dbshell -c "SELECT 1;"

# Check Celery workers
echo "Checking Celery workers..."
kubectl exec -it deployment/bflow-celery -n ${NAMESPACE} -- celery -A misapi inspect ping

echo "All health checks passed!"
```

## 10. Backup and Recovery

### 10.1 Backup Strategy

```yaml
# k8s/backup/velero-schedule.yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: bflow-daily-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  template:
    includedNamespaces:
    - bflow
    - bflow-staging
    - bflow-dev
    ttl: 720h  # 30 days retention
    storageLocation: default
    volumeSnapshotLocations:
    - default
    hooks:
      resources:
      - name: mysql-backup
        includedNamespaces:
        - bflow
        labelSelector:
          matchLabels:
            app: mysql
        pre:
        - exec:
            container: mysql
            command:
            - /bin/bash
            - -c
            - |
              mysqldump --all-databases --single-transaction \
                --triggers --routines --events \
                -u root -p${MYSQL_ROOT_PASSWORD} \
                > /backup/mysql-backup-$(date +%Y%m%d-%H%M%S).sql
```

### 10.2 Disaster Recovery Plan

```bash
#!/bin/bash
# scripts/disaster-recovery.sh

set -e

BACKUP_NAME=$1
TARGET_NAMESPACE=$2

echo "Starting disaster recovery from backup: ${BACKUP_NAME}"

# Restore from Velero backup
velero restore create --from-backup ${BACKUP_NAME} \
  --include-namespaces ${TARGET_NAMESPACE} \
  --wait

# Wait for pods to be ready
kubectl wait --for=condition=ready pod --all -n ${TARGET_NAMESPACE} --timeout=600s

# Verify data integrity
echo "Verifying data integrity..."
kubectl exec -it deployment/bflow-api -n ${TARGET_NAMESPACE} -- \
  python manage.py check_data_integrity

# Run migrations if needed
kubectl exec -it deployment/bflow-api -n ${TARGET_NAMESPACE} -- \
  python manage.py migrate --noinput

echo "Disaster recovery completed!"
```

## 11. Security Hardening

### 11.1 Network Policies

```yaml
# k8s/security/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bflow-api-netpol
  namespace: bflow
spec:
  podSelector:
    matchLabels:
      app: bflow-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    - podSelector:
        matchLabels:
          app: bflow-celery
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mysql
    ports:
    - protocol: TCP
      port: 3306
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - podSelector:
        matchLabels:
          app: rabbitmq
    ports:
    - protocol: TCP
      port: 5672
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

### 11.2 Pod Security Standards

```yaml
# k8s/security/pod-security.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: bflow
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted

---
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: bflow-restricted
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'projected'
  - 'secret'
  - 'downwardAPI'
  - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  supplementalGroups:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: false
```

## 12. Performance Tuning

### 12.1 Application Performance

```python
# settings/production.py
# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'connect_timeout': 10,
            'read_timeout': 10,
            'write_timeout': 10,
            'max_connections': 100,
            'wait_timeout': 28800,
            'interactive_timeout': 28800,
        },
        'CONN_MAX_AGE': 60,
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis-cluster:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
                'socket_keepalive': True,
                'socket_keepalive_options': {},
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'bflow',
        'TIMEOUT': 300,
    }
}

# Celery optimization
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_COMPRESSION = 'gzip'
CELERY_RESULT_COMPRESSION = 'gzip'
CELERY_MESSAGE_COMPRESSION = 'gzip'
```

### 12.2 Kubernetes Resource Tuning

```yaml
# k8s/performance/resource-tuning.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: bflow-quota
  namespace: bflow
spec:
  hard:
    requests.cpu: "50"
    requests.memory: "100Gi"
    limits.cpu: "100"
    limits.memory: "200Gi"
    persistentvolumeclaims: "10"
    services.loadbalancers: "2"

---
apiVersion: v1
kind: LimitRange
metadata:
  name: bflow-limits
  namespace: bflow
spec:
  limits:
  - max:
      cpu: "4"
      memory: "8Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "250m"
      memory: "256Mi"
    type: Container
```

## 13. Troubleshooting Guide

### 13.1 Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Pod CrashLoopBackOff** | Pod keeps restarting | Check logs: `kubectl logs <pod> -n bflow --previous` |
| **Database Connection Error** | 500 errors, connection refused | Verify database pod status and credentials |
| **High Memory Usage** | OOMKilled pods | Increase memory limits or optimize queries |
| **Slow API Response** | Response time > 5s | Check database indexes and query performance |
| **Celery Tasks Not Processing** | Tasks stuck in queue | Verify RabbitMQ connection and worker status |

### 13.2 Debug Commands

```bash
# Get pod logs
kubectl logs -f deployment/bflow-api -n bflow

# Describe pod for events
kubectl describe pod <pod-name> -n bflow

# Execute commands in pod
kubectl exec -it deployment/bflow-api -n bflow -- /bin/bash

# Check resource usage
kubectl top pods -n bflow
kubectl top nodes

# View recent events
kubectl get events -n bflow --sort-by='.lastTimestamp'

# Database queries
kubectl exec -it mysql-cluster-0 -n bflow -- mysql -u root -p

# Redis CLI
kubectl exec -it redis-cluster-0 -n bflow -- redis-cli

# RabbitMQ management
kubectl port-forward svc/rabbitmq-cluster 15672:15672 -n bflow
```

## 14. Maintenance Procedures

### 14.1 Regular Maintenance Tasks

```yaml
# k8s/maintenance/cronjobs.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-optimization
  namespace: bflow
spec:
  schedule: "0 3 * * 0"  # Weekly on Sunday at 3 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: mysql-optimize
            image: mysql:8.0
            command:
            - /bin/bash
            - -c
            - |
              mysqlcheck --optimize --all-databases \
                -h mysql-cluster \
                -u root -p${MYSQL_ROOT_PASSWORD}
          restartPolicy: OnFailure

---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup-old-files
  namespace: bflow
spec:
  schedule: "0 4 * * *"  # Daily at 4 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: registry.gitlab.com/bflow/api:latest
            command:
            - python
            - manage.py
            - cleanup_old_files
            - --days=30
          restartPolicy: OnFailure
```

### 14.2 Certificate Renewal

```bash
#!/bin/bash
# scripts/renew-certificates.sh

set -e

NAMESPACE=$1

echo "Checking certificate expiration..."

# Check certificate status
kubectl get certificate -n ${NAMESPACE} -o json | \
  jq -r '.items[] | select(.status.notAfter < (now + 2592000)) | .metadata.name'

# Force renewal if needed
kubectl annotate certificate bflow-tls \
  cert-manager.io/issue-temporary-certificate="true" \
  -n ${NAMESPACE} --overwrite

# Wait for new certificate
kubectl wait --for=condition=ready certificate/bflow-tls -n ${NAMESPACE}

echo "Certificate renewal completed!"
```

## 15. Documentation

### 15.1 Deployment Checklist

- [ ] Infrastructure provisioned
- [ ] Kubernetes cluster configured
- [ ] Namespaces created
- [ ] Secrets and ConfigMaps applied
- [ ] Databases deployed and initialized
- [ ] Application images built and pushed
- [ ] Deployments created
- [ ] Services exposed
- [ ] Ingress configured
- [ ] SSL certificates issued
- [ ] Monitoring stack deployed
- [ ] Backup solution configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated

### 15.2 Contacts

| Role | Name | Contact | Responsibility |
|------|------|---------|----------------|
| DevOps Lead | [Name] | devops@bflow.com | Infrastructure & Deployment |
| SRE On-Call | [Team] | oncall@bflow.com | 24/7 Support |
| Security Team | [Team] | security@bflow.com | Security Issues |
| Database Admin | [Name] | dba@bflow.com | Database Issues |

---
**Document Control:**
- Version: 1.0
- Last Updated: 2025-07-25
- Review Cycle: Quarterly
- Approval: DevOps Team Lead, Infrastructure Manager