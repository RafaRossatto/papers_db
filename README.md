# 📚 Papers DB

**Papers DB** é uma biblioteca digital inteligente para armazenar e gerenciar artigos acadêmicos sumarizados no formato JSON. O projeto utiliza **PostgreSQL** com suporte nativo a JSONB, permitindo buscas eficientes e consultas estruturadas sobre metadados e resumos.

---

## 🎯 Objetivo

Criar uma base de dados persistente para armazenar artigos, papers e documentos com suas respectivas sumarizações, permitindo futuramente:

- Consultas por palavras-chave, autores, temas
- Decisões automatizadas baseadas no conteúdo dos JSONs
- Integração com scripts Python para inserção e análise

---

## 🧱 Tecnologias Utilizadas

| Ferramenta       | Versão     | Finalidade                          |
|------------------|------------|--------------------------------------|
| Docker           | 24+        | Containerização do banco de dados   |
| Docker Compose   | 2.20+      | Orquestração do ambiente             |
| PostgreSQL       | 18 (latest)| Banco relacional com suporte a JSONB|

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado
- [Docker Compose](https://docs.docker.com/compose/install/) instalado

### 2. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/papers_db.git
cd papers_db