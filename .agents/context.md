# Contexte de la session

Date : 2026-10-25. Dépôt : `/root/git/TMNT` (cluster ARM, Ansible, k3s/microk8s).

## Environnement

- Fuseau : heure de l'Est (`America/Toronto`, EDT jusqu'au 2026-11-01 à 02:00, puis EST). Ne pas utiliser UTC dans les réponses, les notes ni les tâches OpenSpec ; convertir les horodatages des journaux et de Prometheus (UTC) avant de les consigner.
- Inventaire : `inventories/tmnt/` (hôtes `c0`, `c1` dans le groupe `workshop`, DietPi ; groupes `k8s_master` / `k8s_agent`).
- Cibles Debian/Armbian/DietPi : gestionnaire `apt`.

## Matériel (cartes Orange Pi)

| Carte | RAM | Coeurs | Hôtes (champ `model` de `inventories/tmnt/hosts.yml`) |
| --- | --- | --- | --- |
| Orange Pi 3B | 8 Go | 4 | `b0`, `b1`, `b2`, `b4`, `b5` (groupe `worker`, `b3` commenté) |
| Orange Pi 5 Max | 16 Go | 8 | `b6` (groupe `master`) |
| Orange Pi 5 | 16 Go | 8 | `c0` (groupe `workshop`) |
| Mini PC Intel | non précisé | non précisé | `plex` (groupe `autres`, hors cluster k8s) |

- ArgoCD : l'utilisateur le garde (confirmé le 2026-10-31, remplace la décision du 2026-10-25). `minecraft` et `retroassembly` y sont déployés (Synced/Healthy). Le rôle `roles/argocd`, `playbooks/argocd*.yml` et `argocd-apps/` restent utilisés.
- `ansible.cfg` : pipelining, ControlPersist, `forks = 100`.
- Lancement via `Makefile` (`make init`, `make k3s`, `make k8s-reset`, ...).

## Travaux réalisés

### Node.js dans le rôle `init`
- Installation via NodeSource (version `init_nodejs_major_version`, défaut 22), npm inclus.
- Installation uniquement si `node --version` échoue (tag `nodejs`).
- Playbook `playbooks/nodejs.yml` créé puis supprimé (remplacé par le rôle).

### Optimisation du rôle `init` (plan : `docs/plan/init-role-optimisation.md`)
- Cache apt : un seul rafraîchissement ; autres `update_cache` retirés ou remplacés par `cache_valid_time`.
- Mises à niveau optionnelles : `init_upgrade_packages` (défaut `true`), tag `upgrade`.
- Hostname : `ansible.builtin.hostname` pour tous les OS.
- Avahi : `started` + `enabled` (plus de redémarrage systématique).
- Paquets : `stress` et `iperf` retirés ; boucle `omit` remplacée par une liste. `htop`/`btop`, `ansible`, `nfs-kernel-server`, `snapd`, `xtables-addons-common` conservés.
- Helm : 2 tâches, version via `init_helm_version` (`v3.12.0`).
- `fileglob` basés sur `playbook_dir` ; `changed_when: false` sur le bootstrap Python ; cache apt et upgrade regroupés dans un bloc.
- Syntaxe vérifiée ; `make init` lancé par l'utilisateur (code retour 0).

### Kubernetes
- `kubernetes_distribution` par défaut : `k3s` (`inventories/tmnt/group_vars/all.yml`). `make microk8s` reste possible.
- `kubernetes_version` : `v1.37.1+k3s1` (canal `latest`). Le canal `stable` est à `v1.36.5+k3s1`.
  - Attention : passer de 1.35 à 1.37 saute une version mineure (non supporté en mise à niveau sur place).
- Plan d'optimisation k3s : `docs/plan/k3s-install-optimisation.md`, appliqué (syntaxe et expressions Jinja vérifiées, rien exécuté sur le cluster).
  - `roles/k3s/tasks/main.yml` réécrit ; nouveaux `templates/config.yaml.j2` et `handlers/main.yml` ; nouvelles variables dans `defaults/main.yml`.
  - `playbooks/k8s.yml` en 3 plays : masters (`serial: 1`), agents (`k3s_agents_serial`, défaut `100%`), microk8s.
  - Sécurité : token masqué (`no_log`), kubeconfig en mode 600, plus de `/tmp/k3s.yaml`, copie locale dans `logs/kubeconfigs/`.
  - Installation uniquement si binaire absent ou version différente ; garde-fou contre le saut d'une version mineure.
  - UFW via `community.general.ufw` (`kubernetes_ufw_rules` devient une liste de dictionnaires).
  - Non faits : option binaire/checksum, téléchargement centralisé ; `k3s_disable` ajouté mais vide.

### Monitoring et certificats (2026-10-31)
- Monitoring : 12 règles d'alerte (`roles/monitoring/files/alerting_rules.yml`), scrape Longhorn, dashboards Longhorn et Traefik ; `make monitoring` écrit `logs/monitoring/info.txt` (URL, identifiants).
- cert-manager v1.21.3 déployé via ArgoCD (`argocd-apps/cert-manager/application.yaml`, `make cert-manager`). Aucun `ClusterIssuer` pour l'instant : les Ingress utilisent toujours le secret `charlesmenard-com-tls` (acme.sh manuel).

### Plan OpenSpec (2026-10-31)
- OpenSpec 1.16.0 installé (`npm -g`), initialisé avec `--tools none --language fr` (pas de `.github`). Config : `openspec/config.yaml`.
- OpenSpec : `add-quality-checks`, `cleanup-legacy-code`, `harden-ansible-idempotency`, `unify-gitops-deployment` et `deploy-llm-npu` sont terminés et archivés le 2026-10-31 (`openspec/changes/archive/`, specs principales dans `openspec/specs/`). Reste actif : `harden-k8s-workloads` (6.1, contrôle de 24 h). `deploy-llm-npu` (LLM sur le NPU, modèle, Open WebUI) archivé : runtime RKLLM 1.3.1 épinglé, `ollama` en `privileged` justifié. `openspec validate --all --strict` passe.
- Point du 2026-10-31 (soir) : `unify-gitops-deployment` terminé (racine `make argocd-apps` appliquée, secret `tmnt-repo-ssh` supprimé) ; `harden-k8s-workloads` 5/8 (restent 3.2 Minecraft/Crafty, 5.1 SFTP Jellyfin, 6.1 vérification d'ensemble) ; `deploy-llm-npu` 2/7 : modèle `qwen3-1.7b.rkllm` installé par le Job `llm-model-download` de `llm.yml`, `ghcr-pull-secret` créé ; le NPU reste bloqué (containerd ignore l'annotation CDI posée sur le pod ; pistes : device plugin ou `privileged` justifié), donc `ollama` en `CrashLoopBackOff` et `make llm` expire. Les cibles Make de RetroAssembly : `make jeux`.
- Non couverts : secrets (consigne utilisateur), `ClusterIssuer` cert-manager (attend la réponse sur l'API DNS GoDaddy).
- Avancement : `add-quality-checks`, `cleanup-legacy-code` et `harden-ansible-idempotency` terminés ; `unify-gitops-deployment` 11/14 (code prêt, restent 3.1 vérification, 3.2 adoption, 4.3 suppression du secret SSH : tout dépend du push) ; `harden-k8s-workloads` : code local écrit (1.2 et 3.1 cochées ; `scripts/check-images.sh` dans `make lint` ; label `tmnt/class` via `k3s_node_labels` ; probes, `securityContext`, ingress Traefik, images épinglées) ; `make lint` passe. Reste 1.1 (pas de Prometheus), puis la vérification des autres tâches après `make k3s` et le push. Constat du 2026-10-31 : `kubectl` sur `c0` (`~/.kube/config`) pointe vers un ancien cluster (nœuds de 217 j) ; le vrai cluster se lit par `ssh b6 'sudo k3s kubectl ...'` (7 nœuds `Ready`, v1.37.1, applications `cert-manager`/`minecraft`/`retroassembly` Synced/Healthy). Mesures Prometheus relevées (1.1) : retroassembly consomme 1,6 Gio, Minecraft 1,7 Gio, Crafty 0,97 Gio. Label `tmnt/class=rk3588` posé sur `b6` (k3s redémarré par l'utilisateur) ; `git push` du commit `7f35918` fait. Incident du 2026-10-31 (après `git push` de `7f35918`, `make llm`) : `ghcr-pull-secret` n'était créé que par `llm-rknn-build.yml` (maintenant aussi par `llm.yml`, via `github_token`) ; les Deployments à PVC RWO (`minecraft`, `crafty`, `retroassembly`, `open-webui`) étaient en `RollingUpdate` : nouveau pod bloqué (`FailedAttachVolume`, `session.lock`) pendant que l'ancien tourne, d'où `strategy: Recreate` ajouté ; les Applications `minecraft` et `retroassembly` ont disparu d'ArgoCD (cause non identifiée). NPU sans `privileged` par CDI : `playbooks/npu-cdi.yml` (`make npu-cdi` ; abandonné au profit de `privileged: true` et supprimé le 2026-10-31), annotation `cdi.k8s.io/npu` dans `argocd-apps/llm/deployment.yaml` ; containerd de `b6` : `enableCDI: true`. Aucun commit ni push (décision utilisateur) : ArgoCD lit GitHub `main`, donc rien de `argocd-apps/` n'est effectif sans push.
- Outils : `make deps` (venv `.venv`), `make lint` (yamllint, ansible-lint profil `shared`, `scripts/check-makefile.sh`, syntax-check). Dette connue dans `.ansible-lint-ignore` (à réduire).
- Variables communes dans `inventories/tmnt/group_vars/all.yml` : `kubectl_cmd`, `kubectl_base_cmd`, `helm_kubeconfig_arg`. Logs sous `logs/<app>/<nom de l'inventaire>/`.
- Rôles `argocd` et `longhorn`, playbooks `argocd*.yml`, `monitoring.yml`, `longhorn*.yml` en `kubernetes.core` : `changed=0` à la relance (aussi `headlamp`, `cert-manager`). Pas d'horodatage dans les fichiers de logs écrits.
- Écarts : `geerlingguy.nfs` conservé (importé par `roles/mount`), `longhorn-uninstall.yml` gardé via `make longhorn-destroy`, certificat du proxy ArgoCD déplacé de `/tmp` vers `/etc/ssl/argocd` (rôle `argocd`). `jellyfin-sftp-create-password.yml` converti mais non testé (Jellyfin non déployé).
- ArgoCD (plan 4, code local seulement) : `Application` par dossier `argocd-apps/<app>/application.yaml` (exclut son propre fichier), racine `argocd-apps/root.yaml` (`make argocd-apps`), valeurs Jellyfin dans `values.yaml` (`$values`), PVC en `Prune=false`, ingress retroassembly statique Traefik. Playbooks `minecraft`, `retroassembly-app`, `llm`, `jellyfin` (nouveau, remplace `jellyfin-helm.yml`) : namespace + secrets + `Application` uniquement (partie communes dans `playbooks/tasks/`). Dépôt GitHub privé : accès via secret HTTPS (token du vault). Seul `make minecraft` a été relancé en réel ; `retroassembly`, `llm`, `jellyfin` non exécutés avant le push.
- `kubectl` ne doit pas être lancé sur `c0` (README) : seules des lectures ponctuelles via `~/.kube/config` ont été faites.

## Dossier `.agents`

- Dossier d'agents sans `.git` propre, **suivi par le dépôt TMNT** depuis le 2026-10-25 (retiré du `.gitignore`). Ce fichier (`context.md`) y a été déplacé. Point d'entrée : `.agents/AGENT.md` (référencé par `.agents/copilot-instructions.md`).
- Nettoyé le 2026-10-25 : tout ce qui ne s'applique pas a été supprimé (compétences `skills/`, produits/équipes, Jira/Confluence/Google, conventions Django/Airflow/Nuxt, connaissances d'entreprise sur l'infrastructure, agents non Kubernetes/Docker). **Sauvegarde complète : `/root/agents-backup-20261025.tgz`** (restauration : `tar xzf ... -C /root/git/TMNT`).
- Reste : `AGENT.md`, `README.md`, `copilot-instructions.md`, `instructions/` (voir ci-dessous), `agents/infrastructure-expert.agent.md`, `agents/container-image-expert.agent.md`, `knowledge/generic/` (`kubernetes_workload_guidelines.md`, `kubernetes_iac_templates.md`, `dockerfile_ci_templates.md`).
- Appliqué à ce dépôt :
  - Ton : collègue développeur junior, direct et concis, sans superlatifs ni excuses répétées.
  - Kubernetes : `requests` et `limits` obligatoires, `securityContext` (`runAsNonRoot`, capabilities retirées), sondes liveness sans dépendances externes.
  - GitHub : CLI `gh` ; moindre privilège pour RBAC.
- La règle sur les secrets a été retirée à la demande de l'utilisateur (AGENT.md et agent infrastructure). Elle ne s'applique donc plus ; `kubernetes_iac_templates.md` garde toutefois un exemple Sealed Secrets, et `container-image-expert` des consignes sur les secrets dans les images.
- Instructions par fichier (`applyTo`) : déplacées de `.github/instructions/` vers `.agents/instructions/` le 2026-10-25 (Ansible, Debian, Makefile, fichiers prompt, fichiers instructions). `.github` a été **supprimé** (le lien symbolique vers `.agents` a été retiré le 2026-10-26). Le chargement passe par le réglage de l'espace de travail `chat.instructionsFilesLocations` (`.vscode/settings.json`). `.agents/copilot-instructions.md` n'est donc plus chargé automatiquement. Ne pas recréer de dossier `.github`.
- La consigne « base de connaissances en anglais » vise `.agents/knowledge/` ; la documentation de ce dépôt reste en français.

## Points d'attention

- **Jeton Headlamp refusé (2026-10-26)** : `logs/headlamp/tmnt/token.txt` datait du 29 avril (ancien cluster, avant le reset k3s) ; le secret `headlamp-admin-token` du cluster actuel est différent. Fichier régénéré avec `playbooks/headlamp-token.yml` (empreinte identique au secret). Après chaque reset du cluster, relancer `make headlamp-token`. Le message de ce playbook mentionne encore `http://<ip>:30080` (NodePort désactivé) ; l'accès réel est `https://headlamp.home.charlesmenard.com`. Non corrigé.

- **`NXDOMAIN` sur `headlamp.home` (2026-10-26)** : simple faute de frappe (`charlesmenad.com`). Le DNS de l'utilisateur résout correctement `*.home.charlesmenard.com` vers `192.168.0.156` : pas de filtre anti-rebinding sur son réseau.

- **`make ssl-validate` échoue : `Incorrect TXT record` (2026-10-26)** : les TXT publiés chez GoDaddy sont ceux d'une ancienne commande ; le dernier `make ssl-renew` (01:16 UTC) en a généré de nouveaux (voir `logs/ssl/acme-challenge.log`). Il faut mettre à jour `_acme-challenge.k3s` et `_acme-challenge.home` avec ces valeurs, **sans relancer `make ssl-renew`** (chaque lancement crée de nouvelles valeurs), puis `make ssl-validate`, puis `make ssl-deploy`. Défaut du rôle `acme-cert` (corrigé le 2026-10-26) : l'extraction (`grep ... | tail -1`) n'affichait qu'un seul TXT ; elle produit maintenant la liste complète (un nom/valeur par domaine joker) dans `logs/ssl/dns-info.txt` et le message. Syntaxe vérifiée et extraction testée sur le journal existant ; rôle non relancé (`acme.sh` non exécuté). Le certificat actuel couvre `*.k3s.charlesmenard.com` et `*.home.charlesmenard.com`, pas `*.charlesmenard.com` (un joker ne couvre qu'un niveau).

- **Noms DNS (précisé par l'utilisateur le 2026-10-26)** : `*.k3s.charlesmenard.com` sert aux liens **externes** (résout vers l'IP publique) ; `*.home.charlesmenard.com` sert aux accès **internes** au réseau local (résout vers `192.168.0.156`). Exemple Headlamp : `headlamp.k3s.charlesmenard.com` (externe), `headlamp.home.charlesmenard.com` (interne). Les ingress du dépôt déclarent les deux (`headlamp_ingress_hostname` et `headlamp_ingress_hostname_home`).

- **Headlamp inaccessible sur `http://192.168.0.156:30080/` (2026-10-26)** : normal, `playbooks/headlamp.yml` impose `headlamp_nodeport_enabled: false` (service `ClusterIP`, accès par ingress Traefik uniquement). Accès fonctionnel : `https://headlamp.home.charlesmenard.com` (DNS local → `192.168.0.156`) ; `headlamp.k3s.charlesmenard.com` résout vers une IP publique (`70.83.148.71`). HTTP (port 80) renvoie 404. Le secret TLS `charlesmenard-com-tls` n'existe pas dans le namespace `headlamp` : Traefik sert son certificat par défaut (avertissement navigateur) ; `make ssl-deploy` (`playbooks/ssl-certs.yml`) le déploie. NodePort réactivable avec `-e headlamp_nodeport_enabled=true` (non fait).

- **Headlamp : `Wait for Headlamp deployment to be ready` expire (2026-10-26)** : deux causes distinctes, diagnostiquées en lecture seule.
  - Image `ghcr.io/headlamp-k8s/headlamp:v0.41.0` : `ImagePullBackOff` sur `b6`, `403 Forbidden` sur `https://ghcr.io/token`. Transitoire : un `crictl pull` manuel réussit ensuite et le pod passe `Running`. Probable limitation de ghcr (tous les nœuds tirent des images en même temps après le reset). Relancer `playbooks/headlamp.yml`.
  - Réseau des pods sur `b1`, `b2`, `b5` : `FailedCreatePodSandBox`, `iptables ... CHAIN_ADD failed ... POSTROUTING` (plugin `portmap`), pods `svclb-traefik` bloqués en `ContainerCreating` depuis 3 h. Ces trois nœuds tournent sur le noyau `6.18.29` alors que `6.18.54` est installé (`b0`, `b4` ont redémarré et fonctionnent) ; sur `b1`, un seul module `nf_nat`/`nft_chain_nat` est chargé contre deux sur `b0`. **Action utilisateur proposée** : redémarrer `b1`, `b2`, `b5` un par un (`ansible-playbook -i inventories/tmnt/ playbooks/reboot.yml --limit b1 -e nbr_per_batch=1`, etc.). Non fait par l'assistant (interrompt Longhorn et les pods).

- **`playbooks/work` supprimé (2026-10-26)** : `data_drive.yml`, `swarm.yml` et `tmnt_data_drive.yml` supprimés (`git rm`, indexés, non commités). `tmnt_data_drive.yml` avait été renommé un temps en `playbooks/format_and_mount_drive.yml`, puis supprimé : le rôle `mount` (appelé par `init.yml`) fait le même travail. Rien dans le dépôt ne les référençait. Les rôles `swarm` et `portainer` existent toujours (obsolètes).

- **Init de `b3` (2026-10-25)** : `mount : Create nfs directory` échouait (`NoneType has no len()`), car `nfs_volumes_list:` est vide (None) dans `group_vars/all.yml`. Corrigé dans `roles/mount/tasks/nfs.yml` (`default([], true)`). Syntaxe vérifiée, `make init` à relancer.

- **Blocage `Install the agent` (diagnostiqué le 2026-10-25)** : microk8s tourne encore sur le master `b6` (kubelite, containerd, k8s-dqlite, port 16443). k3s y boucle en crash (`10257: address already in use`, 121 redémarrages), donc les agents attendent indéfiniment le superviseur sur `127.0.0.1:6444`.
  - Correctif dans le rôle : contrôle "Refuse to run next to microk8s" (échec rapide), `wait_for` sur l'API du master avant l'installation des agents, `INSTALL_K3S_SKIP_START` + démarrage par `systemd` avec `timeout` (300 s), `timeout: 600` sur les installations.
  - Test réel : `ansible-playbook ... --limit b6` échoue désormais en quelques secondes avec le message attendu.
  - **À faire (action utilisateur)** : `make microk8s-uninstall` (ou `-clean`), puis `make k3s`. Non exécuté par l'assistant : cela détruit le cluster microk8s en cours (pods Longhorn, Crafty, ...).
  - Le service `k3s` de `b6` et `k3s-agent` de `b0` restent en boucle de redémarrage tant que microk8s n'est pas retiré.
- `git diff` montre des suppressions non faites par l'assistant : `docs/acme-ssl-guide.md`, `argocd-ingress-guide.md`, `longhorn-guide.md`, `overlayfs.html`, `ssl-certificates-guide.md`, et une modification de `inventories/tmnt/hosts.yml`. À vérifier avant commit.
- Mots de passe en clair dans `group_vars/all.yml` (`argocd_admin_password`, `jellyfin_admin_password`) : constaté ; l'utilisateur a retiré la règle sur les secrets, ne pas le re-signaler.
- Aucun playbook de ce travail n'a été exécuté par l'assistant, hormis les vérifications de syntaxe et des tests Jinja dans `/tmp`.
- La mise à niveau k3s 1.35 -> 1.37 sera refusée par le garde-fou : passer par `v1.36.5+k3s1`.
- Le kubeconfig du master n'est plus renommé sur place (seule la copie locale l'est).

## Conventions de travail

- Mettre à jour ce fichier (`.agents/context.md`) à chaque changement de contexte.
- Mettre à jour les plans de `docs/plan/` après chaque point appliqué.

## Prochaines étapes

1. Valider `make init` sur `c0` puis un second passage (`changed=0`).
2. Tester `make k3s` sur un cluster réduit (`--check --diff --limit`), puis un second passage (`changed=0`).
3. Choisir la version k3s (`latest` ou `stable`) en tenant compte du garde-fou.

---

## Contexte du projet : token_counter

### Demande
Calculer les tokens restants à consommer par jour ouvrable jusqu'à la fin du mois, et affiner « Par jour » et « À épargner » (compter ou non le jour courant, simuler une date).

### Environnement constaté
- Python 3.9+, aucune dépendance externe. Tests : `python3 -m unittest discover -s tests`.
- Package `token_counter/` : `config.py`, `calendar_utils.py`, `budget.py` (fonctions pures), `cli.py`. Lancement : `python -m token_counter <tokens_utilises> [--config f] [--debug_date AAAA-MM-JJ]`.
- `config.json` (ignoré par git) : `total_tokens`, `holidays`, `exclude_today` (défaut `false`), `debug_date` (défaut `null`).
- Workflow : OpenSpec (`openspec/changes/`, schéma spec-driven, artefacts en français). Vocabulaire : « jours ouvrables » (et non « ouvrés »).

### Réalisé (non committé)
- Change `add-token-budget-calculator` : calculateur initial (11/11 tâches), prêt à archiver.
- Change `improve-daily-budget-today` : clé `exclude_today` ; à `true`, la journée en cours est terminée et les jours restants partent de demain (0 si demain change de mois). « Par jour » et « À épargner » utilisent le même nombre de jours ; l'hypothèse est affichée (8/8 tâches).
- Change `add-debug-date` : date simulée via `--debug_date` ou `debug_date` du JSON ; précédence CLI > JSON > date réelle ; ligne « Date simulée » affichée (6/6 tâches).
- Hors change : renommage « ouvré » → « ouvrable » (code, README, tests, specs), libellés de sortie réalignés, calendrier élargi (cases de 6 caractères).
- Tests : 32 OK ; `openspec validate --all` OK.

### Décisions
- Un plafonnement du « Quota normal par jour » aux tokens restants le dernier jour a été essayé puis annulé à la demande de l'utilisateur : ne pas le réintroduire.
- Défaut conservé : aujourd'hui compte comme jour restant.

### Reste à faire (utilisateur)
1. Retirer `debug_date` de `config.json` pour revenir à la date réelle.
2. Archiver les changes terminés (`/opsx-archive`) ; les specs ne sont pas encore synchronisés dans `openspec/specs/`.
3. Committer les modifications.
