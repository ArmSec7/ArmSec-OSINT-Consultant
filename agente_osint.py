import os
import warnings
from dotenv import load_dotenv

load_dotenv()

# Imports enxutos, usando apenas o que realmente precisamos (sem o módulo problemático 'chains')
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate

warnings.filterwarnings("ignore")

# ==========================================
# 1. BASE DE CONHECIMENTO (EXPANDIDA E CATEGORIZADA)
# ==========================================
banco_de_ferramentas = [
    {
        "nome": "Amass (OWASP)",
        "categoria": "Mapeamento Avançado de Rede",
        "descricao": "Realiza mapeamento de rede profundo e descoberta de ativos externos usando raspagem de dados, APIs e DNS bruto. Essencial para descobrir ASNs, blocos de IP e subdomínios.",
        "uso": "amass enum -d dominio.com"
    },
    {
        "nome": "crt.sh",
        "categoria": "Enumeração Passiva de Subdomínios",
        "descricao": "Base de dados online de Certificate Transparency. Permite descobrir subdomínios registrados de forma 100% passiva, analisando certificados SSL/TLS públicos.",
        "uso": "Acessar https://crt.sh/?q=%.dominio.com"
    },
    {
        "nome": "Shodan",
        "categoria": "Buscador de Dispositivos Conectados",
        "descricao": "Mapeia a internet procurando portas abertas, banners de serviços, roteadores vulneráveis e infraestrutura exposta. Ideal para reconhecimento passivo de IPs.",
        "uso": "No site ou CLI: shodan search 'hostname:empresa.com'"
    },
    {
        "nome": "theHarvester",
        "categoria": "Coleta de E-mails e Superfície de Ataque",
        "descricao": "Busca e-mails, nomes e URLs em fontes abertas (Google, LinkedIn, PGP). Excelente para a fase inicial de reconhecimento e mapeamento de funcionários para engenharia social.",
        "uso": "theHarvester -d empresa.com -b all"
    },
    {
        "nome": "HaveIBeenPwned (HIBP)",
        "categoria": "Análise de Vazamentos",
        "descricao": "Plataforma líder para verificar se endereços de e-mail ou domínios foram expostos em brechas de dados conhecidas.",
        "uso": "Acessar haveibeenpwned.com ou consultar via scripts consumindo a API."
    },
    {
        "nome": "Sherlock",
        "categoria": "SOCMINT (Investigação de Redes Sociais)",
        "descricao": "Busca por um nome de usuário (username) em mais de 300 redes sociais e fóruns. Ótimo para rastrear a pegada digital de um alvo rapidamente.",
        "uso": "python3 sherlock.py nome_do_alvo"
    },
    {
        "nome": "ExifTool",
        "categoria": "Análise de Metadados (Forense/OSINT)",
        "descricao": "Extrai metadados ocultos (EXIF) de imagens, PDFs e documentos. Pode revelar datas de criação, modelo da câmera, coordenadas GPS e softwares utilizados.",
        "uso": "exiftool documento.pdf"
    },
    {
        "nome": "Maltego",
        "categoria": "Análise Visual de Links e Grafos",
        "descricao": "Plataforma que integra dezenas de fontes de dados (transforms) para criar gráficos visuais das relações entre pessoas, empresas, domínios e IPs.",
        "uso": "Interface Gráfica. Exige criação de conta na Community Edition (CE)."
    },
    {
        "nome": "Recon-ng",
        "categoria": "Framework de Reconhecimento Web",
        "descricao": "Framework modular similar ao Metasploit, focado exclusivamente em OSINT web. Usa módulos independentes para consultar APIs e bancos de dados de forma organizada.",
        "uso": "recon-ng (no terminal)"
    },
    {
        "nome": "Google Dorks (GHDB)",
        "categoria": "Busca Avançada Operacional",
        "descricao": "Uso de operadores matemáticos e lógicos no Google para contornar a indexação padrão e achar painéis administrativos, diretórios abertos ou arquivos confidenciais.",
        "uso": "No buscador: site:alvo.com ext:pdf \"confidencial\""
    }
]

documentos = []
for ferramenta in banco_de_ferramentas:
    conteudo = f"Ferramenta: {ferramenta['nome']}\nCategoria: {ferramenta['categoria']}\nDescrição: {ferramenta['descricao']}\nComando de Uso: {ferramenta['uso']}"
    documentos.append(Document(page_content=conteudo))

# ==========================================
# 2. MOTOR RAG (VETORIZAÇÃO E RECUPERAÇÃO)
# ==========================================
print("[*] ArmSec Osint Agent carregando módulos de reconhecimento...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
banco_vetorial = Chroma.from_documents(documentos, embeddings)

# Traz as 3 ferramentas mais relevantes
recuperador = banco_vetorial.as_retriever(search_kwargs={"k": 3})

# ==========================================
# 3. CÉREBRO (LLM) E PROMPT DE IDENTIDADE
# ==========================================
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.1)

template_prompt = """
Você é o ArmSec Osint Agent Consultor, um mentor virtual especializado em Inteligência de Fontes Abertas e fundamentos de cibersegurança tática.
Sua missão é instruir o operador sobre a melhor estratégia de reconhecimento, usando como base as ferramentas do seu contexto local.

REGRAS DE CONDUTA:
1. Analise o cenário e recomende a melhor abordagem usando APENAS o contexto fornecido.
2. Destaque claramente se a técnica sugerida é de reconhecimento PASSIVO ou ATIVO.
3. SE A SOLUÇÃO NÃO ESTIVER NO CONTEXTO: Indique especificamente o site **OSINT Framework (osintframework.com)** ou o **Google Hacking Database (GHDB)**.

Contexto de Ferramentas ArmSec:
{context}

Cenário reportado pelo operador: {question}

Estruture seu relatório da seguinte forma:
- **Estratégia Recomendada:** [Visão geral de como resolver o problema]
- **Ferramenta(s) do Arsenal:** [Nomes das ferramentas locais que se aplicam, se houver]
- **Execução Tática:** [Comandos e exemplos práticos]
- **Nota de OPSEC:** [Aviso sobre os rastros e interações diretas com o alvo]
"""
prompt = PromptTemplate(template=template_prompt, input_variables=["context", "question"])

# ==========================================
# 4. INTERFACE DE COMANDO
# ==========================================
def exibir_banner():
    banner = r"""
    ======================================================
     ___            ___             _   _   ___   ___ 
    |   \  _ _  _  / __| ___  __   /_\ | | / __| / _ \ 
    | |) || '_|| | \__ \/ -_)/ _| / _ \| || (__ | (_) |
    |___/ |_|  |_| |___/\___|\__|/_/ \_\_| \___| \___/ 
                                                    
      ArmSec OSINT Consultant Agent v2.0 - Active
    ======================================================
    """
    print(banner)

exibir_banner()
print("[+] Módulo de Inteligência iniciado. Digite 'sair' para encerrar a sessão.")

while True:
    cenario = input("\n[Operador] Defina o vetor de ataque ou objetivo de coleta: ")
    if cenario.lower() == 'sair':
        print("\n[ArmSec Agent] Sessão encerrada. OPSEC mantida.")
        break
    
    print("\n[ArmSec Agent] Triando vetores e consultando matriz de ferramentas...")
  
    try:
        # 1. Pega os arquivos do banco de dados (retriever)
        docs_recuperados = recuperador.invoke(cenario)
        
        # 2. Junta o texto deles
        texto_contexto = "\n\n".join([doc.page_content for doc in docs_recuperados])
        
        # 3. Cria a pergunta final
        pergunta_final = prompt.format(context=texto_contexto, question=cenario)
        
        # 4. Manda pro Google Gemini responder
        resposta = llm.invoke(pergunta_final)
        
        print("-" * 70)
        
        # --- FILTRO DE LIMPEZA DE TEXTO ---
        conteudo = resposta.content
        
        # Se a API mandou como uma lista estruturada
        if isinstance(conteudo, list):
            print(conteudo[0].get('text', str(conteudo)))
            
        # Se a API mandou como uma string bruta de dicionário (o que rolou no seu terminal)
        elif isinstance(conteudo, str) and conteudo.startswith("[{'type':"):
            import ast
            try:
                blocos = ast.literal_eval(conteudo)
                print(blocos[0].get('text', conteudo))
            except:
                print(conteudo)
                
        # Se vier limpo padrão
        else:
            print(conteudo)
        # ----------------------------------
        
        print("-" * 70)
        
    except Exception as e:
        print(f"\n[!] Falha de link com o núcleo LLM: {e}")