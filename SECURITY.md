# Política de segurança

## Escopo deste repositório

Aqui há **documentação**, **listas de links** e **workflows de CI** (verificação de links). Não publicamos binários nem serviços como produto. Mesmo assim, queremos tratar com seriedade **conteúdo malicioso** e **falhas que afetem quem clona ou executa os workflows**.

## O que consideramos in-scope

- **Links** nos arquivos Markdown que levem a phishing, malware ou conteúdo ilegal.
- **Pull requests** ou issues que tentem injetar scripts ofuscados, workflows perigosos ou roubo de segredos.
- **Workflows** (`.github/workflows/`) com passos que exponham `GITHUB_TOKEN` ou dados sensíveis de forma indevida.

## Fora de escopo

- Vulnerabilidades em **sites de terceiros** citados nas listas (Coursera, YouTube, etc.) — reporte ao responsável de cada plataforma.
- Segurança do **seu** ambiente local ou do **GitHub** em geral — use os canais oficiais do GitHub quando couber.

## Como reportar

1. Prefira **[Report a vulnerability](https://docs.github.com/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)** (avisos de segurança privados), se a opção estiver ativada no repositório.
2. Se não houver botão de relatório privado, abra uma issue com título claro (ex.: `security:`) **sem** incluir exploit completo em público até haver triagem; ou use o contato que os mantenedores indicarem no README, se existir.

Inclua: descrição, passos para reproduzir, impacto presumido e, se aplicável, sugestão de correção.

## Tempo de resposta

Trataremos relatórios críticos (malware, vazamento de segredos) com prioridade. Este é um projeto de currículo mantido de forma voluntária; prazos exatos dependem da disponibilidade de quem mantém o fork.

## Divulgação responsável

Pedimos que **não divulgue** detalhes que permitam abuso em massa antes de correção ou esclarecimento mútuo, salvo quando já houver risco público conhecido.
