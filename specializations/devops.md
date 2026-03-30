# Especialização: DevOps / plataforma / SRE (introdução forte)

## Pré-requisitos mínimos

- Redes, SO, programação II, banco de dados; desejável sistemas distribuídos.

## Trilha sugerida

1. **Linux** — systemd, permissões, processos, rede em CLI.
2. **Contêineres** — Docker/Podman; imagens multi-stage; não rodar como root.
3. **IaC** — Terraform ou Ansible em projeto pequeno mas real.
4. **CI/CD** — pipeline com testes, build, deploy em ambiente de homologação.
5. **Observabilidade** — logs estruturados, métricas (Prometheus ou similar), um painel.
6. **Confiabilidade** — SLI/SLO em papel; error budget explicado.

## Recursos

- [SadServers](https://sadservers.com/), documentação de Kubernetes (se for o caminho).
- *Designing Data-Intensive Applications* (Kleppmann) para dados em produção.

## Capstone

- **A:** Três serviços em compose com healthcheck, rede interna e reverse proxy.
- **B:** Cluster mínimo (k3d/minikube) com deploy declarativo e rollback documentado.

## Prova de nível

Runbook de incidente simulado (post-mortem sem culpa) + diagrama de arquitetura atualizado no repo.
