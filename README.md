# 🛒 E-commerce Data Pipeline: End-to-End ELT & Analytics

Este repositório contém a construção de uma pipeline de dados completa para um e-commerce, indo da extração de dados brutos até a visualização final em um dashboard interativo. O foco principal deste projeto é aplicar as melhores práticas de Engenharia de Dados, utilizando armazenamento em nuvem e a Arquitetura Medalhão para governança e qualidade de dados.

## 🛠️ Stack Tecnológica
* **Linguagem:** Python (Pandas)
* **Cloud Data Warehouse:** PostgreSQL (Supabase)
* **Transformação & Orquestração:** dbt (Data Build Tool)
* **Visualização:** Python Web App (Dashboard)

## 🏗️ Arquitetura do Projeto (ELT)

O fluxo de dados foi desenhado seguindo a abordagem **ELT (Extract, Load, Transform)**, garantindo que as regras de negócio fiquem centralizadas e blindadas dentro do banco de dados:

1. **Extract & Load (Ingestão):** Leitura de dados brutos a partir de arquivos `.parquet` utilizando Python/Pandas, realizando a carga inicial no schema `public` do Supabase.
2. **Transform (Arquitetura Medalhão com dbt):** Orquestração das transformações em três camadas:
    * 🥉 **Bronze:** Views espelhando os dados originais (histórico imutável).
    * 🥈 **Silver:** Tabelas higienizadas, com tipagem corrigida e deduplicação. A "fonte da verdade".
    * 🥇 **Gold (`gold_sales`):** Data Marts consolidados. Agregações e KPIs de negócio (como receita, ticket médio e volume por período) prontos para consumo.
3. **Analytics (Visualização):** Um aplicativo em Python conectando diretamente na camada Gold para exibir as métricas aos tomadores de decisão.

## 📂 Estrutura do Repositório

A organização do projeto reflete a separação de responsabilidades entre infraestrutura, modelagem e produto:

* `/docs/` - Documentação de negócio e requisitos (PRDs do dbt e do Dashboard).
* `/scripts/` - Scripts Python de extração/ingestão e arquivos SQL de configuração do banco.
* `/dbt_transformations/` - Todo o projeto dbt, contendo a modelagem das camadas Bronze, Silver e Gold.
* `/dashboard/` - Código-fonte do aplicativo de visualização final (`app.py`).
* `/data/` - Arquivos de origem e base de dados bruta.

## 💼 Visão de Negócio (PRDs)
A tecnologia deve servir ao negócio. Para entender os requisitos, regras e o problema que este pipeline resolve, consulte nossos Product Requirements Documents (PRDs):
* [📄 PRD - Arquitetura Medalhão (dbt)](docs/prd_dbt_medalhao.md)
* [📄 PRD - Dashboard de Vendas](docs/prd_dashboard_vendas.md)

---
*Projeto desenvolvido para consolidar conhecimentos avançados em Engenharia e Análise de Dados.*
*Agradecimento especial a Jornada de Dados - Luciano Vasconcelos.*
