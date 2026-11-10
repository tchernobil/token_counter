# Agent configuration

- `context.md`: running project context (hardware, work done, open points). Keep it up to date.
- `AGENT.md`: persona, guidelines, knowledge index (loaded through `copilot-instructions.md`).
- `instructions/`: file-scoped Copilot instructions (moved from `.github/`, which no longer exists; loaded via `chat.instructionsFilesLocations`).
- `agents/`: `infrastructure-expert` (Kubernetes workloads), `container-image-expert` (Dockerfiles, multi-arch, CI).
- `knowledge/generic/`: Kubernetes workload guidelines, Kubernetes and Dockerfile/CI templates.
