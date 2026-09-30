import sys
import os

# Garante que o pacote raiz seja encontrado quando executado da pasta frontend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from core.blockchain import Blockchain
from core.certificate_data import CertificateData
from contracts.academic_contract import AcademicSmartContract
import hashlib
from datetime import datetime
import io
from PIL import Image

# ─────────────────────────────────────────────
# Configuração da página
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Blockchain de Certificados Acadêmicos",
    page_icon="🔗",
    layout="wide"
)

# ─────────────────────────────────────────────
# CSS Customizado — Tema Verde Blockchain
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Reset global para usar Inter */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* Cabeçalho principal */
h1 {
    background: linear-gradient(135deg, #10b981, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800 !important;
}

h2, h3 {
    color: #6ee7b7 !important;
    font-weight: 700 !important;
}

/* Botões primários */
div.stButton > button[kind="primary"],
div.stFormSubmitButton > button[kind="primary"] {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    border: none !important;
    color: #ecfdf5 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 16px rgba(16, 185, 129, 0.3) !important;
}

div.stButton > button[kind="primary"]:hover,
div.stFormSubmitButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 24px rgba(16, 185, 129, 0.5) !important;
}

/* Botões secundários */
div.stButton > button:not([kind="primary"]) {
    border-color: #163636 !important;
    color: #6ee7b7 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

div.stButton > button:not([kind="primary"]):hover {
    border-color: #10b981 !important;
    color: #34d399 !important;
    background: rgba(16, 185, 129, 0.08) !important;
}

/* Métrica na sidebar */
[data-testid="stMetricValue"] {
    color: #10b981 !important;
    font-weight: 700 !important;
}

/* Expander com estilo de bloco */
[data-testid="stExpander"] {
    border: 1px solid #163636 !important;
    border-radius: 10px !important;
    background: rgba(12, 26, 26, 0.5) !important;
}

/* Barra de progresso do Streamlit */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #059669, #10b981, #34d399) !important;
}

/* Radio buttons como tabs */
div[role="radiogroup"] {
    gap: 0.5rem !important;
}

/* Code blocks */
code {
    background: rgba(16, 185, 129, 0.1) !important;
    color: #34d399 !important;
    border-radius: 4px !important;
    padding: 0.15rem 0.4rem !important;
    font-size: 0.88em !important;
}

/* Badge de bloco */
.block-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.6rem;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 9999px;
    color: #34d399;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 0.75rem;
}

.block-badge::before {
    content: '';
    width: 6px;
    height: 6px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 6px #10b981;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Inicialização do estado da sessão
# ─────────────────────────────────────────────
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain(difficulty=3)

if 'contract' not in st.session_state:
    st.session_state.contract = AcademicSmartContract(admin_role="secretaria_uea")

if 'query_target' not in st.session_state:
    st.session_state.query_target = {"doc_hash": None, "cert_id": None}


def hash_file_data(file_bytes):
    """
    Gera o hash SHA-256 dos bytes do arquivo (PDF ou imagem).
    """
    return hashlib.sha256(file_bytes).hexdigest()


# ─────────────────────────────────────────────
# Barra Lateral (Sidebar)
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="block-badge">BLOCKCHAIN CERTIFICADOS UEA</div>', unsafe_allow_html=True)
    st.header("⚙️ Configurações & Acesso")

    # Seletor de Perfil para simulação de permissões
    user_role = st.selectbox(
        "Perfil Ativo (Simulação):",
        options=["secretaria_uea", "aluno_publico"],
        format_func=lambda x: (
            "🏛️ Secretaria Acadêmica (Admin)" if x == "secretaria_uea"
            else "🎓 Aluno / Público (Sem Permissão)"
        )
    )

    st.markdown("---")
    st.header("ℹ️ Sobre o Sistema")
    st.markdown("""
    Este sistema utiliza **Blockchain local** e **Contrato Inteligente** para registro,
    verificação e ciclo de vida de certificados acadêmicos.

    **Características:**
    - 🔒 **Privacidade & Eficiência:** Apenas hashes e metadados essenciais
    - 📝 **Contrato Inteligente:** Valida permissões e impede duplicidades
    - 🔗 **Imutabilidade:** Prova matemática contra fraudes

    **Como testar:**
    1. **Emissão Válida:** Como Secretaria, emita um certificado
    2. **Sem Permissão:** Mude para Aluno e tente emitir
    3. **Duplicidade:** Registre o mesmo documento duas vezes
    4. **Revogação:** Na aba Consulta, revogue um certificado
    """)

    st.markdown("---")

    # Métricas da blockchain
    total_blocos = len(st.session_state.blockchain.blocks)
    delta_blocos = total_blocos - 1  # blocos além do gênesis
    st.metric(
        "Total de Blocos",
        total_blocos,
        delta=f"+{delta_blocos} desde o gênesis" if delta_blocos > 0 else "Apenas bloco gênesis"
    )
    st.metric("Dificuldade de Mineração (PoW)", st.session_state.blockchain.difficulty)

    st.markdown("---")
    if st.button("🔄 Reiniciar Blockchain", use_container_width=True):
        st.session_state.blockchain = Blockchain(difficulty=3)
        st.session_state.contract = AcademicSmartContract(admin_role="secretaria_uea")
        st.session_state.query_target = {"doc_hash": None, "cert_id": None}
        st.toast("✅ Blockchain e Contrato reiniciados para o Bloco Gênesis!")
        st.rerun()

# ─────────────────────────────────────────────
# Título Principal
# ─────────────────────────────────────────────
st.title("🔗 Blockchain de Certificados Acadêmicos")
st.caption("Sistema de emissão, validação e revogação de certificados com Smart Contract — UEA")

st.markdown("---")

# ─────────────────────────────────────────────
# Abas de Navegação
# ─────────────────────────────────────────────
tabs = ["📝 Registro", "🔍 Consulta & Validação", "⛓ Blockchain"]
selected_tab = st.radio("", tabs, horizontal=True, label_visibility="collapsed")

# ─────────────────────────────────────────────
# ABA 1: REGISTRO (EMISSÃO)
# ─────────────────────────────────────────────
if selected_tab == "📝 Registro":
    st.header("📝 Registrar Novo Certificado Acadêmico")
    st.caption("Apenas a Secretaria Acadêmica autorizada possui permissão para emitir novos certificados.")

    with st.form("certificate_form"):
        col1, col2 = st.columns(2)
        with col1:
            cert_id = st.text_input("Código do Certificado *", placeholder="Ex: UEA-CERT-2026-001")
            student_id = st.text_input("Matrícula do Aluno *", placeholder="Ex: 2021001234")
        with col2:
            student_name = st.text_input("Nome Completo do Aluno *", placeholder="Ex: Maria Oliveira")
            course = st.text_input("Curso / Evento *", placeholder="Ex: Engenharia de Software")

        uploaded_file = st.file_uploader(
            "📎 Selecione o arquivo do certificado (PDF, Imagem)",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            key="cert_file"
        )

        # Preview se for imagem
        if uploaded_file is not None:
            if uploaded_file.type.startswith('image'):
                try:
                    img = Image.open(uploaded_file)
                    st.image(img, caption="Preview do Documento", width=350)
                except Exception:
                    pass
            else:
                st.info(f"📄 Arquivo selecionado: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

        submitted = st.form_submit_button("⛏ Registrar na Blockchain", type="primary", use_container_width=True)

        if submitted:
            if not cert_id or not student_id or not student_name or not course:
                st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
            elif uploaded_file is None:
                st.error("⚠️ Por favor, selecione um arquivo de certificado.")
            else:
                file_bytes = uploaded_file.getvalue()
                doc_hash = hash_file_data(file_bytes)

                cert_data = CertificateData(
                    cert_id=cert_id.strip(),
                    student_id=student_id.strip(),
                    student_name=student_name.strip(),
                    course=course.strip(),
                    document_hash=doc_hash,
                    issuer=user_role
                )

                # Submete ao Contrato Inteligente
                try:
                    is_valid_tx, msg = st.session_state.contract.issue_certificate(user_role, cert_data)

                    # Mineração com feedback visual de progresso
                    progress_bar = st.progress(0, text="Iniciando mineração Proof-of-Work...")
                    import time
                    for i in range(1, 4):
                        time.sleep(0.3)
                        progress_bar.progress(i * 25, text=f"Minerando... calculando nonce ({i * 25}%)")

                    with st.spinner("Finalizando e selando bloco..."):
                        new_block = st.session_state.blockchain.new_block(cert_data)
                        st.session_state.blockchain.add_block(new_block)

                    progress_bar.progress(100, text="Bloco minerado com sucesso! ✅")
                    time.sleep(0.5)
                    progress_bar.empty()

                    st.success("✅ Certificado aprovado pelo Contrato Inteligente e gravado com sucesso!")

                    col_r1, col_r2 = st.columns(2)
                    with col_r1:
                        st.info(f"**Bloco #{new_block.index}** minerado | Nonce: `{new_block.nonce}`")
                    with col_r2:
                        st.caption(f"Hash SHA-256 do Documento: `{doc_hash[:32]}...`")

                    st.balloons()

                except (PermissionError, ValueError) as err:
                    st.error(f"🛑 **Rejeição pelo Contrato Inteligente:**\n\n{str(err)}")

# ─────────────────────────────────────────────
# ABA 2: CONSULTA & VALIDAÇÃO
# ─────────────────────────────────────────────
elif selected_tab == "🔍 Consulta & Validação":
    st.header("🔍 Consultar e Validar Certificado")
    st.caption("Verifique a autenticidade e o estado atual de um certificado através de arquivo ou código.")

    query_mode = st.radio(
        "Método de Consulta:",
        ["📁 Por Upload do Arquivo", "🔑 Por Código do Certificado"],
        horizontal=True
    )

    doc_hash_to_query = None
    cert_id_to_query = None

    if query_mode == "📁 Por Upload do Arquivo":
        verify_file = st.file_uploader(
            "Envie o documento para calcular a assinatura digital e conferir:",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            key="verify_file"
        )
        if verify_file is not None:
            doc_hash_to_query = hash_file_data(verify_file.getvalue())
            st.code(f"Hash SHA-256 calculado: {doc_hash_to_query}", language="text")
    else:
        cert_id_to_query = st.text_input("Digite o Código do Certificado:", placeholder="Ex: UEA-CERT-2026-001")

    if st.button("🔍 Consultar Estado na Blockchain", type="primary"):
        if not doc_hash_to_query and not (cert_id_to_query and cert_id_to_query.strip()):
            st.warning("⚠️ Por favor, selecione um arquivo ou digite um código de certificado.")
            st.session_state.query_target = {"doc_hash": None, "cert_id": None}
        else:
            st.session_state.query_target = {
                "doc_hash": doc_hash_to_query,
                "cert_id": cert_id_to_query.strip() if cert_id_to_query else None
            }

    # Avaliação do alvo consultado persistido na sessão
    target = st.session_state.query_target
    if target["doc_hash"] or target["cert_id"]:
        result = st.session_state.contract.verify_certificate(
            document_hash=target["doc_hash"],
            cert_id=target["cert_id"]
        )

        if result["valid"]:
            data = result["data"]
            st.success("✅ Certificado Autêntico e Válido!")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Código:** `{data['cert_id']}`")
                st.markdown(f"**Aluno:** {data['student_name']}")
                st.markdown(f"**Matrícula:** `{data['student_id']}`")
            with col_b:
                st.markdown(f"**Curso:** {data['course']}")
                st.markdown(f"**Data de Emissão:** {data['issue_date']}")
                st.markdown(f"**Status:** :green[{data['status']}]")
                st.markdown(f"**Emissor:** `{data['issuer']}`")

            st.caption(f"Hash do Documento: `{data['document_hash']}`")

            # Ação de Revogação (Apenas se logado como Secretaria)
            st.markdown("---")
            st.subheader("🔄 Gerenciamento de Ciclo de Vida")
            if user_role == "secretaria_uea":
                with st.expander("⚠️ Revogar este Certificado", expanded=True):
                    reason = st.text_input(
                        "Motivo da revogação:",
                        value="Inconsistência documental",
                        key="revoke_reason"
                    )
                    if st.button("🛑 Confirmar Revogação", type="primary", key="btn_confirm_revoke"):
                        try:
                            revoked_cert, msg = st.session_state.contract.revoke_certificate(
                                caller_role=user_role,
                                cert_id_or_hash=data['cert_id'],
                                reason=reason
                            )
                            # Grava a revogação como novo bloco na blockchain
                            rev_block = st.session_state.blockchain.new_block(revoked_cert)
                            st.session_state.blockchain.add_block(rev_block)
                            st.warning(f"⚠️ {msg}")
                            st.info(
                                f"Alteração de estado gravada no **Bloco #{rev_block.index}** "
                                f"(Hash: `{rev_block.hash[:20]}...`)"
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao revogar: {e}")
            else:
                st.info("💡 Apenas o perfil **Secretaria Acadêmica** pode executar a revogação de certificados.")

        elif result["status"] == "REVOGADO":
            data = result["data"]
            st.error("🛑 ATENÇÃO: Este certificado foi **REVOGADO**!")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown(f"**Código:** `{data['cert_id']}`")
                st.markdown(f"**Aluno:** {data['student_name']}")
                st.markdown(f"**Status:** :red[REVOGADO]")
            with col_r2:
                st.markdown(f"**Data da Revogação:** {data.get('revocation_date')}")
                st.markdown(f"**Motivo:** {data.get('revocation_reason')}")
            st.caption(f"Hash do Documento: `{data['document_hash']}`")
        else:
            st.error("❌ Documento **NÃO encontrado**! O arquivo não foi registrado ou foi adulterado.")

# ─────────────────────────────────────────────
# ABA 3: BLOCKCHAIN
# ─────────────────────────────────────────────
elif selected_tab == "⛓ Blockchain":
    st.header("⛓ Estado da Blockchain Local")

    # Exibir status de integridade
    is_valid = st.session_state.blockchain.is_blockchain_valid()
    if is_valid:
        st.success("✅ **Integridade da Blockchain:** Cadeia Válida — nenhum bloco adulterado")
    else:
        st.error("❌ **Alerta:** A Blockchain foi violada ou contém blocos inconsistentes!")

    st.subheader(f"📦 Blocos da Blockchain ({len(st.session_state.blockchain.blocks)} total)")

    for block in st.session_state.blockchain.blocks:
        # Expande apenas o bloco mais recente automaticamente
        is_latest = block.index == len(st.session_state.blockchain.blocks) - 1
        label = f"📦 Bloco #{block.index}" + (" — Gênesis" if block.index == 0 else "") + (" 🆕" if is_latest and block.index > 0 else "")

        with st.expander(label, expanded=is_latest):
            col_b1, col_b2 = st.columns([2, 1])
            with col_b1:
                st.markdown(f"**Hash Anterior:** `{block.previous_hash}`")
                st.markdown(f"**Hash do Bloco:** `{block.hash}`")
            with col_b2:
                ts = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                st.markdown(f"**Timestamp:** {ts}")
                st.markdown(f"**Nonce (PoW):** `{block.nonce}`")
            st.markdown(f"**Dados:** {block.data}")
