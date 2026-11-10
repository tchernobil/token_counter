# Kubernetes Workload Guidelines

This document outlines the engineering standards and best practices for deploying workloads (Pods, Deployments, StatefulSets) to our Kubernetes clusters.

Unlike traditional VM or basic Docker environments, Kubernetes enforces strict resource boundaries using Linux `cgroups`. Understanding these boundaries is critical to service stability.

---

## 1. Resource Management (Requests vs. Limits)

Always define both `requests` and `limits` for CPU and Memory to ensure Quality of Service (QoS).

### 1.1 CPU
*   **Requests:** The guaranteed amount of CPU a pod needs. Kubernetes uses this to schedule the pod on a node with enough available capacity.
*   **Limits:** The maximum CPU a pod can use.
    *   *Warning:* Exceeding the CPU limit results in **CPU Throttling** (the process is artificially slowed down by the kernel), which leads to severe latency spikes but *not* a crash.
    *   *Best Practice:* For latency-sensitive APIs, it is often better to keep CPU requests and limits close to each other, or avoid limits entirely if the node is dedicated, to prevent unexpected throttling during traffic spikes.

### 1.2 Memory
*   **Requests:** The guaranteed memory for the pod.
*   **Limits:** The absolute hard ceiling for memory usage.
    *   *Danger:* If a container attempts to allocate even 1 byte above its memory limit, the Linux kernel will instantly terminate it with an **OOMKilled** (Out Of Memory) status. There is no throttling for memory; it is binary.

---

## 2. In-Memory Data Stores (Redis / Valkey)

Deploying in-memory data stores like Redis or Valkey in Kubernetes requires special attention to avoid unexpected `OOMKilled` crashes, which are often mistakenly attributed to application bugs.

### The BGSAVE (Fork) Problem
Redis/Valkey uses a background process (`BGSAVE`) to snapshot data to disk (RDB).
1.  It creates a child process (fork).
2.  Linux uses *Copy-on-Write*. If the parent process modifies data while the child is saving, the memory page is duplicated.
3.  **Result:** During high write traffic, the total memory footprint of the container can temporarily **double** during a snapshot.

### Deployment Rules for Redis/Valkey
To prevent OOMKilled crashes during snapshots:

1.  **Generous Kubernetes Limits:** The K8s `memory` limit MUST be significantly higher than the intended working dataset size (often 1.5x to 2x) to absorb the fork spike. Never set a limit like `192Mi` for a production cache.
2.  **Internal Memory Boundary (`maxmemory`):** You MUST configure the internal `maxmemory` parameter of the Redis/Valkey server. If you do not tell the application its limits, it will assume it has access to the entire node's RAM and will inevitably hit the Kubernetes hard limit.
3.  **Eviction Policy:** Always set a `maxmemory-policy` so the application knows how to shed data when it reaches its internal limit, rather than crashing.

**Example (Correct Configuration):**
```yaml
# In the Kubernetes Deployment/StatefulSet
resources:
  requests:
    memory: 256Mi
  limits:
    memory: 512Mi  # 512Mi hard limit allows room for the BGSAVE fork

# In the container arguments (or redis.conf)
args:
  - "redis-server"
  - "--maxmemory 350mb" # Stop accepting/evict keys at 350mb
  - "--maxmemory-policy allkeys-lru" # Evict least recently used keys
```

---

## 3. Health Probes (Liveness & Readiness)

Probes are a cornerstone of creating self-sufficient and resilient services on Kubernetes. They allow the system to detect failures and self-heal without human intervention. Properly configured probes dictate how Kubernetes routes traffic and restarts unhealthy pods.

*   **Liveness Probes:** "Is the application completely dead or deadlocked?"
    *   If this fails, Kubernetes *restarts* the container.
    *   Do NOT check external dependencies (like a database connection) in a liveness probe. If the database goes down, restarting your API pod will not fix the database, it will only cause a cascading failure of restarts.
*   **Readiness Probes:** "Is the application ready to receive HTTP traffic?"
    *   If this fails, Kubernetes stops sending traffic to the pod (removes it from the Service endpoint).
    *   This is the correct place to check external dependencies (DBs, caches) or to wait for initial cache loading/warmup.