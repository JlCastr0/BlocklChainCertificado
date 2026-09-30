# 🔗 Blockchain de Certificados Acadêmicos

**Universidade do Estado do Amazonas (UEA)**  
**Disciplina:** Oficina de Desenvolvimento de Sistemas 3  
**Docente:** Prof. Fábio Santos

**Equipe:**
- João Lucas
- Pedro Yutaro
- Lucas Carvalho

---

## 1. Definição do Problema

A falsificação e adulteração de diplomas universitários e certificados de conclusão de curso representam um problema crônico no Brasil.

Dados de investigações da Polícia Federal e do Ministério da Educação (MEC) estimam que **mais de 100.000 diplomas e certificados falsos** circulam anualmente no país, com cobranças que variam entre R$ 2.000 e R$ 20.000 por documento adulterado — colocando em risco áreas essenciais como medicina, engenharia e advocacia.

### Limitações dos Modelos Tradicionais

- **Vulnerabilidade documental:** PDFs e documentos impressos são facilmente adulterados com ferramentas básicas de edição, sem deixar marcas visíveis.
- **Verificação lenta e burocrática:** Empresas e órgãos públicos levam semanas contatando secretarias acadêmicas para atestar a autenticidade de um diploma.
- **Ponto único de falha:** Bancos de dados relacionais (SQL/NoSQL) dependem de controle centralizado. Um usuário com privilégio de administrador pode alterar ou deletar registros retroativamente sem auditoria matemática independente.

---

## 2. A Solução: Registro em Blockchain com Smart Contract

A solução consiste em um sistema baseado em **Blockchain local** e **Contrato Inteligente**, permitindo que a instituição registre documentos de forma inviolável e que qualquer terceiro verifique a autenticidade em segundos.

### Por que Blockchain e não um Banco de Dados Comum?

| Característica | Banco de Dados SQL | Blockchain Local |
|:---|:---:|:---:|
| Permite UPDATE / DELETE | ✅ Sim | ❌ Não (append-only) |
| Adulteração retroativa possível | ✅ Sim | ❌ Detectável matematicamente |
| Auditoria independente | ❌ Não | ✅ Sim (hashes encadeados) |
| Prova de existência com timestamp | ❌ Não | ✅ Sim |

---

## 3. Modelagem de Dados: On-Chain vs. Off-Chain

Para garantir conformidade com a **LGPD** e preservar o desempenho da rede:

| Tipo | Dado | Onde Fica | Justificativa |
|:---|:---|:---|:---|
| **On-Chain** | Hash SHA-256 do Documento | Dentro do Bloco | Impressão digital de 64 caracteres — prova a integridade sem armazenar o arquivo |
| **On-Chain** | Código, Matrícula, Curso e Emissor | Dentro do Bloco | Metadados públicos para indexação e consulta rápida |
| **On-Chain** | Estado (`ATIVO` / `REVOGADO`) | Dentro do Bloco | Transparência do ciclo de vida do certificado |
| **Off-Chain** | Arquivo PDF / Imagem | Armazenamento local | Evita blockchain bloat — arquivos pesados inviabilizam a mineração |
| **Off-Chain** | Dados pessoais sensíveis (RG, CPF, Notas) | Fora da cadeia | Conformidade LGPD — a imutabilidade impediria o direito ao esquecimento |

---

## 4. Arquitetura do Sistema

A aplicação é organizada em **3 camadas desacopladas** e **4 pacotes Python**:

```
BlocklChainCertificado/
│
├── core/                          # Motor da Blockchain (lógica pura)
│   ├── block.py                   # Estrutura do Bloco: SHA-256, Nonce, PoW
│   ├── blockchain.py              # Blockchain local e validação da cadeia
│   └── certificate_data.py        # Modelo de dados do Certificado Acadêmico
│
├── contracts/                     # Contrato Inteligente
│   └── academic_contract.py       # Regras de negócio, RBAC e ciclo de vida
│
├── api/                           # Camada de API REST (Flask)
│   └── routes.py                  # Endpoints HTTP para integração externa
│
├── frontend/                      # Interface web
│   ├── streamlit_app.py           # App interativo com tema verde blockchain
│   └── apresentacao.html          # Apresentação de slides HTML (10 slides)
│
├── tests/                         # Testes automatizados
│   └── test_contract.py           # 6 testes cobrindo todos os casos de uso
│
├── main.py                        # Demonstração via terminal (CLI)
├── requirements.txt               # Dependências Python
├── .streamlit/config.toml         # Tema visual verde do Streamlit
└── .gitignore
```

### Regras do Contrato Inteligente (`contracts/academic_contract.py`)

- **Controle de Acesso (RBAC):** Apenas `secretaria_uea` pode emitir e revogar. Tentativas por `aluno_publico` geram `PermissionError`.
- **Anti-Duplicidade:** O contrato impede que o mesmo arquivo (hash) ou código de certificado seja cadastrado mais de uma vez (`ValueError`).
- **Validação Estrutural:** Exige campos obrigatórios preenchidos e hash SHA-256 válido (64 caracteres).
- **Gerenciamento de Ciclo de Vida:** A revogação altera o estado para `REVOGADO` e grava um novo bloco — sem violar a imutabilidade do registro original.

---

## 5. Casos de Uso

### ✅ Operações Aceitas
- **Emissão Autorizada:** Secretaria envia dados consistentes e arquivo inédito → bloco minerado via PoW.
- **Consulta de Autenticidade:** Upload do PDF original → hash comparado → retorna `Certificado Válido e Ativo`.
- **Revogação Administrativa:** Secretaria cancela certificado irregular → novo bloco com `REVOGADO` minerado.

### 🛑 Operações Rejeitadas
- **Acesso Não Autorizado:** Aluno tenta emitir ou revogar → `PermissionError`.
- **Duplicidade de Documento:** Mesmo arquivo enviado duas vezes → `ValueError`.
- **Duplicidade de Código:** Mesmo código institucional reaproveitado → `ValueError`.
- **Documento Adulterado:** PDF modificado na consulta → hash diferente → documento não encontrado.

---

## 6. Instruções de Execução

### Pré-requisitos
- Python 3.8 ou superior

### 1. Criar e ativar o Ambiente Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Executar a Interface Web (Streamlit)

```bash
streamlit run frontend/streamlit_app.py
```

Acesse no navegador: `http://localhost:8501`

### 4. Executar os Testes Automatizados

```bash
python3 tests/test_contract.py
```

> Resultado esperado: **6 testes executados — 100% aprovados**, cobrindo emissão, permissão, duplicidade, adulteração, revogação e corrupção de blocos.

### 5. Executar a Demonstração via Terminal (CLI)

```bash
python3 main.py
```

### 6. Abrir a Apresentação de Slides

```bash
xdg-open frontend/apresentacao.html
```

- **Navegação:** Setas `←` `→` ou barra de `Espaço`
- **Tela Cheia:** Tecla `F` ou botão `Tela Cheia`

### 7. Executar a API REST (Flask) — opcional

```bash
python3 api/routes.py
```

Endpoints disponíveis em `http://localhost:5000`:

| Método | Rota | Descrição |
|:---:|:---|:---|
| `GET` | `/` | Status da API e lista de endpoints |
| `POST` | `/issue` | Emissão de certificado |
| `POST` | `/revoke` | Revogação de certificado |
| `GET` | `/verify` | Consulta por `?cert_id=` ou `?hash=` |
| `GET` | `/blockchain` | Visualização de todos os blocos |

---

## 7. Roteiro para a Apresentação (10 Minutos)

| Tempo | Etapa | Ações |
|:---:|:---|:---|
| **00:00 – 02:00** | Problema, Solução e Justificativa | Apresentar equipe, dado de 100k fraudes, comparativo Blockchain vs SQL, divisão on-chain/off-chain (LGPD) |
| **02:00 – 04:00** | Arquitetura e Smart Contract | Apresentar as 3 camadas, regras de RBAC e anti-duplicidade |
| **04:00 – 08:00** | Demonstração Prática | 1. Emitir certificado → Bloco #1 minerado<br>2. Inspecionar hashes na aba Blockchain<br>3. Mudar para Aluno → tentar emitir (acesso negado)<br>4. Tentar mesmo arquivo → duplicidade rejeitada<br>5. Revogar certificado → status REVOGADO + Bloco #2 |
| **08:00 – 10:00** | Testes e Conclusão | Executar `python3 tests/test_contract.py` mostrando 6/6 aprovados; concluir sobre segurança e transparência |
