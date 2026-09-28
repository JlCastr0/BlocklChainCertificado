# Blockchain de Certificados Acadêmicos

**Universidade do Estado do Amazonas (UEA)**  
**Disciplina:** Oficina de Desenvolvimento de Software 2  
**Docente:** Prof. Dr. Fábio Santos  

**Equipe:**
* João Lucas
* Pedro Yutaro
* Lucas Carvalho

---

## 1. Definição do Problema

A falsificação e adulteração de diplomas universitários e certificados de conclusão de curso representam um problema crônico no Brasil. 

Dados e investigações da Polícia Federal e do Ministério da Educação (MEC) estimam que **mais de 100.000 diplomas e certificados falsos** circulam anualmente no país, abastecendo um mercado paralelo com cobranças que variam entre R$ 2.000 e R$ 20.000 por documento adulterado. Essa prática gera insegurança jurídica e coloca em risco setores essenciais da sociedade, como medicina, enfermagem, engenharia e advocacia.

### Limitações dos Modelos Tradicionais
* **Vulnerabilidade de Documentos Físicos e Digitais:** PDFs e documentos impressos são facilmente adulterados com ferramentas simples de edição gráfica sem deixar marcas visíveis.
* **Lentidão e Burocracia na Verificação:** Empresas, recrutadores e órgãos públicos levam semanas entrando em contato com secretarias acadêmicas para atestar a autenticidade de um diploma.
* **Centralização e Ponto Único de Falha:** Bancos de dados relacionais convencionais (SQL/NoSQL) dependem de permissões centrais. Um usuário com privilégios de administrador (root) pode inserir, alterar ou deletar históricos retroativamente sem que haja uma auditoria matemática independente.

---

## 2. A Solução Proposta e Justificativa da Blockchain

A solução desenvolvida consiste em um sistema descentralizado baseado em **Blockchain local** e **Contrato Inteligente (*Smart Contract*)**, permitindo que a instituição registre e autentique documentos de forma inviolável e que qualquer terceiro verifique a autenticidade do diploma em segundos.

### Por que Blockchain e não um Banco de Dados Comum?
1. **Estrutura Imutável (*Append-Only*):** Uma vez que o bloco contendo a transação do certificado é minerado via algoritmo de consenso *Proof-of-Work* (PoW), ele não pode ser alterado nem excluído. Operações destrutivas como `UPDATE` e `DELETE` não existem na cadeia.
2. **Encadeamento Criptográfico:** Cada bloco armazena o hash criptográfico SHA-256 do bloco anterior (`previous_hash`). Qualquer tentativa de adulterar um registro histórico invalida matematicamente todos os blocos subsequentes da cadeia.
3. **Carimbo de Tempo Confiável (*Timestamping*):** Prova exata de existência do documento naquela data e horário oficial.
4. **Independência de Validação:** Terceiros não precisam de acesso direto ao banco de dados interno da universidade; basta submeter o arquivo do certificado para calcular seu hash e consultar o livro-razão público da Blockchain.

---

## 3. Modelagem de Dados: On-Chain vs. Off-Chain

Para garantir conformidade legal com a LGPD (Lei Geral de Proteção de Dados) e preservar o desempenho da rede evitando o inchaço desnecessário da cadeia (*Blockchain Bloat*), os dados foram rigorosamente divididos:

| Tipo | Dado Armazenado | Onde Fica | Justificativa Técnica |
| :--- | :--- | :--- | :--- |
| **On-Chain** | Hash SHA-256 do Documento | Dentro do Bloco | **Prova Matemática Leve:** Ocupa apenas 64 caracteres hexadecimais (32 bytes). Garante a integridade absoluta do arquivo PDF original sem sobrecarregar a Blockchain. |
| **On-Chain** | Código do Certificado, Matrícula, Curso e Emissor | Dentro do Bloco | **Auditoria Institucional:** Metadados públicos essenciais para indexação rápida, histórico e consultas diretas no livro-razão. |
| **On-Chain** | Estado do Documento (`ATIVO` ou `REVOGADO`) | Dentro do Bloco | **Transparência do Ciclo de Vida:** Garante que anulações de certificados por fraude fiquem registradas publicamente na cadeia. |
| **Off-Chain** | Arquivo Bruto do PDF / Imagem | Fora da Blockchain (Local) | **Prevenção de Blockchain Bloat:** Gravar arquivos pesados (megabytes) degrada a replicação dos nós e inviabiliza a mineração e o consenso. |
| **Off-Chain** | Dados Pessoais Sensíveis (RG, CPF, Notas Detalhadas) | Fora da Blockchain | **Conformidade com a LGPD:** A imutabilidade da Blockchain viola o princípio do "Direito ao Esquecimento" e a exigência legal de exclusão de dados pessoais quando solicitado pelo titular. |

---

## 4. Arquitetura do Sistema e Contrato Inteligente

A aplicação foi projetada em 3 camadas desacopladas:

1. **Camada de Apresentação (Frontend Streamlit):** Interface web intuitiva com abas para Registro de Certificados, Consulta/Validação e Inspeção da Blockchain.
2. **Camada de Regras de Negócio (Smart Contract):** Classe `AcademicSmartContract` que intercepta e valida todas as transações antes da criação de qualquer bloco.
3. **Camada de Consenso e Armazenamento (Blockchain Local):** Motor que executa a mineração com *Proof-of-Work*, encadeia os blocos por SHA-256 e valida a integridade contínua da cadeia.

### Regras de Negócio do Smart Contract (`smart_contract.py`)
* **Controle de Acesso Baseado em Papéis (RBAC):** Apenas identidades com a função de Secretaria Acadêmica (`secretaria_uea`) podem executar emissão (`issue_certificate`) e revogação (`revoke_certificate`). Chamadas feitas por usuários sem permissão (`aluno_publico`) são rejeitadas com erro de permissão (`PermissionError`).
* **Prevenção de Duplicidade (Anti-Fraude):** O contrato impede que um mesmo documento (hash SHA-256) ou um mesmo código de certificado seja cadastrado mais de uma vez (`ValueError`).
* **Validação Estrutural:** Exige que todos os campos obrigatórios estejam preenchidos e que o hash tenha 64 caracteres hexadecimais válidos.
* **Gerenciamento de Ciclo de Vida (Revogação):** Permite que a Secretaria cancele um certificado fraudulento, alterando o estado para `REVOGADO` e gravando um novo bloco de revogação na Blockchain sem violar a imutabilidade do registro original.

---

## 5. Casos de Uso: Operações Válidas vs. Rejeitadas

### Casos Aceitos (Válidos)
* **Emissão Autorizada:** A Secretaria envia dados consistentes e um arquivo inédito. O bloco é minerado com sucesso via PoW.
* **Consulta de Autenticidade:** O usuário faz upload do PDF original. O contrato valida a correspondência do hash e retorna `Certificado Válido e Ativo`.
* **Revogação Administrativa:** A Secretaria detecta irregularidade e aciona a revogação. Um novo bloco é minerado e o status muda para `REVOGADO`.

### Casos Rejeitados (Operações Inválidas e Sem Permissão)
* **Acesso Não Autorizado:** O perfil Aluno tenta emitir um certificado ou revogar um registro existente. A operação é bloqueada com mensagem explícita de acesso negado.
* **Tentativa de Duplicidade de Documento:** Tentar emitir um certificado usando um arquivo PDF que já foi cadastrado anteriormente.
* **Tentativa de Duplicidade de Código:** Tentar emitir um certificado reaproveitando um código institucional já existente.
* **Documento Adulterado:** Submissão de um PDF com alteração de uma única letra na aba de consulta. O hash calculado não coincide com a base e o sistema acusa documento não registrado.

---

## 6. Estrutura de Arquivos

```text
atv1/
├── apresentacao.html          # Apresentação interativa de slides em HTML (sem emojis)
├── REQUISITOS.MD              # Especificação oficial do trabalho da disciplina
├── Blockchain_APP/
│   ├── apresentacao.html      # Cópia local da apresentação de slides
│   ├── block_class.py         # Estrutura do Bloco (SHA-256, Nonce, PoW)
│   ├── blockchain.py          # Lógica da Blockchain local e validação da cadeia
│   ├── certificate_data.py    # Modelo de dados do Certificado Acadêmico
│   ├── smart_contract.py      # Lógica de negócio e permissões (Smart Contract)
│   ├── streamlit_app.py       # Interface Web com Streamlit
│   ├── test_contract.py       # Suíte de testes automatizados (unittest)
│   ├── main.py                # Demonstração via terminal (CLI)
│   ├── app.py                 # API REST em Flask (opcional)
│   ├── requirements.txt       # Dependências Python
│   └── README.md              # Documentação local da pasta
└── BlockchainExemplo/         # Exemplo didático em Java fornecido na aula
```

---

## 7. Instruções de Execução

### Pré-requisitos
* Python 3.8 ou superior instalado.

### 1. Entrar na pasta da aplicação
```bash
cd Blockchain_APP
```

### 2. Ativar o Ambiente Virtual (`.venv`)
O ambiente virtual já está configurado na pasta:
```bash
source .venv/bin/activate
```

*(Caso precise recriar o ambiente do zero:)*
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Executar a Interface Web (Streamlit)
```bash
streamlit run streamlit_app.py
```
Acesse no navegador: `http://localhost:8501`

### 4. Executar os Testes Automatizados
```bash
python3 test_contract.py
```
> Resultado esperado: **6 testes executados e 100% aprovados** cobrindo emissão, permissão, duplicidade, adulteração, revogação e corrupção de blocos.

### 5. Executar a Demonstração via Terminal
```bash
python3 main.py
```

### 6. Abrir a Apresentação de Slides
Abra o arquivo `apresentacao.html` diretamente no seu navegador ou via linha de comando:
```bash
xdg-open apresentacao.html
```
* **Navegação:** Setas `Esquerda` / `Direita` ou barra de `Espaço`.
* **Tela Cheia:** Pressione a tecla `F` ou clique no botão `Tela Cheia`.

---

## 8. Roteiro Cronometrado para a Apresentação (10 Minutos)

| Tempo | Etapa | Ações e Demonstrações |
| :---: | :--- | :--- |
| **00:00 - 02:00**<br>(2 min) | **Problema, Solução e Justificativa** | - Apresentar a equipe (João Lucas, Pedro Yutaro, Lucas Carvalho).<br>- Expor o dado de 100.000 fraudes anuais e o risco de bancos de dados comuns sofrerem alterações manuais.<br>- Explicar a proposta da Blockchain e a divisão dos dados on-chain vs. off-chain (LGPD). |
| **02:00 - 04:00**<br>(2 min) | **Arquitetura e Smart Contract** | - Apresentar as 3 camadas desacopladas (Frontend, Smart Contract, Blockchain).<br>- Detalhar as regras de permissão (apenas Secretaria emite/revoga) e prevenção de duplicidade. |
| **04:00 - 08:00**<br>(4 min) | **Demonstração Prática na Blockchain Local** | 1. **Emissão Válida:** Com perfil Secretaria, emitir um certificado e mostrar o Bloco #1 sendo minerado com Proof-of-Work.<br>2. **Inspeção de Blocos:** Ir na aba Blockchain e mostrar os hashes encadeados.<br>3. **Demonstração de Rejeição (Permissão):** Mudar para o perfil Aluno e tentar emitir novo certificado (mostrar o alerta vermelho de acesso negado).<br>4. **Demonstração de Rejeição (Duplicidade):** Voltar para Secretaria e tentar enviar o mesmo PDF (mostrar erro de documento já registrado).<br>5. **Alteração de Estado (Revogação):** Na aba Consulta & Validação, localizar o certificado e clicar em "Revogar Certificado". Mostrar que o status virou `REVOGADO` e o Bloco #2 foi minerado. |
| **08:00 - 10:00**<br>(2 min) | **Resultados e Conclusão** | - Mostrar a suíte de testes unitários passando no terminal (`python3 test_contract.py`).<br>- Concluir resumindo o ganho de segurança e transparência para a UEA. |
