# Kubernetes & IaC Code Templates

Reference templates for Terraform, Kubernetes manifests, and sealed secrets.
See `knowledge/generic/infrastructure/` files for architectural context.

---

## Terraform

### State Isolation Pattern

```hcl
# Each layer must have its own isolated state backend
terraform {
  backend "s3" {
    bucket = "terraform-state"
    key    = "infra/vpc/terraform.tfstate"   # Layer-specific path
    region = "ca-central-1"
  }
}

# Layer structure:
# terraform/infra/       → Layer 1: Base infrastructure (networking)
# terraform/eks/         → Layer 2: Cluster configuration
# terraform/kubernetes/  → Layer 3: K8s resources
# terraform/modules/     → Shared reusable modules
```

### Module Reuse

```hcl
module "vpc" {
  source      = "../../modules/vpc"
  environment = var.environment
  region      = var.region
}
```

### Variable Validation

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Must be dev, staging, or prod."
  }
}
```

---

## Kubernetes

### Resource Limits (mandatory on all workloads)

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Redis / Valkey Memory (K8s limit must include fork headroom)

```yaml
resources:
  limits:
    memory: "512Mi"          # K8s hard limit
env:
- name: REDIS_ARGS
  value: "--maxmemory 384mb --maxmemory-policy allkeys-lru"
  # 384mb = 75% of 512Mi — leaves 128mb headroom for BGSAVE fork
```

> **Why**: Redis forks a child process during BGSAVE, temporarily doubling memory. Without headroom, K8s OOMKills the pod.

### Health Probes

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3
```

> **Rule**: Liveness must NOT check downstream dependencies — a DB outage would restart all pods simultaneously.

### Security Context

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop: [ALL]
  readOnlyRootFilesystem: true
```

### Deployment (stateless)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      containers:
      - name: api
        image: api-server:1.2.3    # Never :latest
        resources: ...             # Always set
        livenessProbe: ...
        readinessProbe: ...
        securityContext: ...
```

### StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
spec:
  serviceName: redis
  replicas: 1
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cleanup-job
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: cleanup
            image: cleanup-tool:1.0.0
```

---

## Sealed Secrets

```bash
# 1. Create plaintext secret (DO NOT commit)
kubectl create secret generic my-secret \
  --from-literal=api-key=super-secret-value \
  --dry-run=client -o yaml > secret.yaml

# 2. Seal it
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# 3. Commit sealed-secret.yaml — safe to version control
git add sealed-secret.yaml

# 4. Delete plaintext
rm secret.yaml
```

```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: my-secret
  namespace: production
spec:
  encryptedData:
    api-key: AgBy8+k3F...    # Encrypted value
```

---

## GitOps (Argo CD)

```yaml
# Development — auto-sync
spec:
  syncPolicy:
    automated:
      prune: true
      selfHeal: true

# Production — manual approval required
spec:
  syncPolicy:
    automated: null
```

---

## DNS Naming Convention

Pattern: `{service}.{environment}.{domain}.cbc.ca`

```
mediafiles.dev.ema.cbc.ca
terminus.prod.ema.cbc.ca
airflow.staging.ema.cbc.ca
```
