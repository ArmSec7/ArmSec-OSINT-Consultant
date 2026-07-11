<<<<<<< HEAD
# 🕵️‍♂️ ArmSec OSINT Agent Consultor

O **ArmSec OSINT Agent** é um assistente virtual especializado em Inteligência de Fontes Abertas (OSINT) e segurança cibernética tática. Projetado para atuar como um mentor técnico, ele utiliza arquitetura RAG (Retrieval-Augmented Generation) com Google Gemini para fornecer estratégias de reconhecimento, recomendações de ferramentas e diretrizes de OPSEC baseadas em cenários reais.

## 🚀 Funcionalidades
* **Motor Inteligente:** Base de conhecimento vetorial local (ChromaDB) com Google Gemini.
* **Mentoria Tática:** Recomenda ferramentas específicas para cada vetor de investigação.
* **Segurança Operacional:** Alerta automaticamente sobre o nível de exposição (Reconhecimento Passivo vs. Ativo).
* **Direcionamento Estratégico:** Caso não possua a resposta na base, orienta o operador para as melhores fontes da comunidade global (OSINT Framework, GHDB, etc).

## 🛠️ Instalação

1. Clone o repositório:
   ```bash
   git clone [https://github.com/Armsec7/ArmSec-Osint-Agent.git](https://github.com/Armsec7/ArmSec-Osint-Agent.git)
   cd ArmSec-Osint-Agent


   **Instale as dependências:** 
   pip install -r requirements.txt

   Configure a API Key:

  Renomeie o arquivo .env.example para .env.

  Insira sua chave do Google AI Studio no arquivo: GOOGLE_API_KEY=sua_chave_aqui
   
   **Execute o Agente**
   python agente_osint.py
   
=======
# ArmSec-OSINT-Consultant
Assistente de segurança cibernética para automação de consultas OSINT. Analisa cenários táticos, sugere ferramentas de coleta e mantém o rigor em procedimentos de reconhecimento passivo.
>>>>>>> 78e7937b1cd613e134276a99ce5855ff16d04157
