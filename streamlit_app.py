import streamlit as st
from blockchain import Blockchain
from certificate_data import CertificateData
from smart_contract import AcademicSmartContract
import hashlib
from datetime import datetime
import io
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Blockchain de Certificados Acadêmicos",
    page_icon="🎓",
    layout="wide"
)

# Inicialização da blockchain e do Smart Contract no session_state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain(difficulty=3)

if 'contract' not in st.session_state:
    st.session_state.contract = AcademicSmartContract(admin_role="secretaria_uea")

if 'query_target' not in st.session_state:
    st.session_state.query_target = {"doc_hash": None, "cert_id": None}

def hash_file_data(file_bytes):
    """
    Gera o hash SHA-256 dos bytes do arquivo (PDF ou imagem)
    """
    return hashlib.sha256(file_bytes).hexdigest()

# Barra Lateral (Sidebar)
with st.sidebar:
    st.header("⚙️ Configurações & Acesso")
    
    # Seletor de Perfil para simulação de permissões
    user_role = st.selectbox(
        "Perfil Ativo (Simulação):",
        options=["secretaria_uea", "aluno_publico"],
        format_func=lambda x: "🏛️ Secretaria Acadêmica (Admin)" if x == "secretaria_uea" else "🎓 Aluno / Público (Sem Permissão)"
    )
    
    st.markdown("---")
    st.header("Informações")
    st.markdown("""
    ### Sobre o Sistema
    Este sistema utiliza **Blockchain local** e **Contrato Inteligente** para registro, verificação e ciclo de vida de certificados acadêmicos.
    
    ### Características
    - **Privacidade & Eficiência:** Armazenamento apenas de hashes e metadados essenciais (o PDF/imagem original não sobrecarrega a cadeia).
    - **Contrato Inteligente:** Valida permissões de emissão/revogação e impede duplicidades.
    - **Imutabilidade:** Prova matemática contra fraudes e adulterações.
    
    ### Como testar na apresentação
    1. **Emissão Válida:** Como Secretaria, emita um certificado.
    2. **Tentativa Inválida (Sem Permissão):** Mude o perfil para Aluno e tente emitir. O contrato rejeitará.
    3. **Tentativa Inválida (Duplicidade):** Tente registrar o mesmo documento duas vezes.
    4. **Alteração de Estado:** Na aba de Consulta, revogue um certificado e veja o estado mudar.
    """)
    
    st.markdown("---")
    # Métricas da blockchain
    st.metric("Total de Blocos", len(st.session_state.blockchain.blocks))
    st.metric("Dificuldade de Mineração (PoW)", st.session_state.blockchain.difficulty)

    if st.button("🔄 Reiniciar Blockchain", use_container_width=True):
        st.session_state.blockchain = Blockchain(difficulty=3)
        st.session_state.contract = AcademicSmartContract(admin_role="secretaria_uea")
        st.session_state.query_target = {"doc_hash": None, "cert_id": None}
        st.toast("Blockchain e Contrato reiniciados para o Bloco Gênesis!")
        st.rerun()

# Título Principal
st.title("🎓 Blockchain de Certificados Acadêmicos")

# Abas de Navegação (mantendo a mesma estrutura visual original)
tabs = ["Registro", "Consulta & Validação", "Blockchain"]
selected_tab = st.radio("Selecione uma opção:", tabs, horizontal=True)

# -------------------------------------------------------------
# ABA 1: REGISTRO (EMISSÃO)
# -------------------------------------------------------------
if selected_tab == "Registro":
    st.header("Registrar Novo Certificado Acadêmico")
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
            "Selecione o arquivo do certificado (PDF, Imagem)",
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
                st.info(f"📄 Arquivo selecionado: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        submitted = st.form_submit_button("Registrar na Blockchain")
        
        if submitted:
            if not cert_id or not student_id or not student_name or not course:
                st.error("Por favor, preencha todos os campos obrigatórios.")
            elif uploaded_file is None:
                st.error("Por favor, selecione um arquivo de certificado.")
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
                    
                    # Se o contrato aprovou, minera e adiciona à Blockchain
                    with st.spinner("Minerando novo bloco (Proof-of-Work)..."):
                        new_block = st.session_state.blockchain.new_block(cert_data)
                        st.session_state.blockchain.add_block(new_block)
                        
                    st.success("✅ Certificado aprovado pelo Contrato Inteligente e gravado com sucesso!")
                    st.info(f"**Bloco #{new_block.index}** minerado com sucesso! Hash: `{new_block.hash}`")
                    st.caption(f"Hash SHA-256 do Documento: `{doc_hash}`")
                    st.balloons()
                    
                except (PermissionError, ValueError) as err:
                    # Demonstração clara da rejeição de operação pelo Contrato
                    st.error(f"🛑 Rejeição pelo Contrato Inteligente:\n\n{str(err)}")

# -------------------------------------------------------------
# ABA 2: CONSULTA & VALIDAÇÃO
# -------------------------------------------------------------
elif selected_tab == "Consulta & Validação":
    st.header("Consultar e Validar Certificado")
    st.caption("Verifique a autenticidade e o estado atual de um certificado através de arquivo ou código.")
    
    query_mode = st.radio("Método de Consulta:", ["Por Upload do Arquivo", "Por Código do Certificado"], horizontal=True)
    
    doc_hash_to_query = None
    cert_id_to_query = None
    
    if query_mode == "Por Upload do Arquivo":
        verify_file = st.file_uploader("Envie o documento para calcular a assinatura digital e conferir:", type=['png', 'jpg', 'jpeg', 'pdf'], key="verify_file")
        if verify_file is not None:
            doc_hash_to_query = hash_file_data(verify_file.getvalue())
            st.code(f"Hash SHA-256 calculado: {doc_hash_to_query}", language="text")
    else:
        cert_id_to_query = st.text_input("Digite o Código do Certificado:", placeholder="Ex: UEA-CERT-2026-001")
    
    if st.button("Consultar Estado na Blockchain"):
        if not doc_hash_to_query and not (cert_id_to_query and cert_id_to_query.strip()):
            st.warning("Por favor, selecione um arquivo ou digite um código de certificado.")
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
            
            # Ação de Revogação (Apenas se logado como Secretaria - Demonstração de Alteração de Estado)
            st.markdown("---")
            st.subheader("Gerenciamento de Ciclo de Vida (Secretaria)")
            if user_role == "secretaria_uea":
                with st.expander("Revogar este Certificado", expanded=True):
                    reason = st.text_input("Motivo da revogação:", value="Inconsistência documental", key="revoke_reason")
                    if st.button("Confirmar Revogação", type="primary", key="btn_confirm_revoke"):
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
                            st.info(f"Alteração de estado gravada no Bloco #{rev_block.index} (Hash: `{rev_block.hash[:20]}...`)")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao revogar: {e}")
            else:
                st.info("💡 Apenas o perfil 'Secretaria Acadêmica' pode executar a revogação de certificados.")
                
        elif result["status"] == "REVOGADO":
            data = result["data"]
            st.error("🛑 ATENÇÃO: Este certificado foi REVOGADO!")
            st.markdown(f"**Código:** `{data['cert_id']}` | **Aluno:** {data['student_name']}")
            st.markdown(f"**Status:** :red[REVOGADO]")
            st.markdown(f"**Data da Revogação:** {data.get('revocation_date')}")
            st.markdown(f"**Motivo:** {data.get('revocation_reason')}")
            st.caption(f"Hash do Documento: `{data['document_hash']}`")
        else:
            st.error("❌ Documento NÃO encontrado! O arquivo não foi registrado ou foi adulterado.")

# -------------------------------------------------------------
# ABA 3: BLOCKCHAIN
# -------------------------------------------------------------
elif selected_tab == "Blockchain":
    st.header("Estado da Blockchain Local")
    
    # Exibir status de integridade
    is_valid = st.session_state.blockchain.is_blockchain_valid()
    if is_valid:
        st.success("✅ Integridade da Blockchain: Cadeia Válida (Nenhum bloco adulterado)")
    else:
        st.error("❌ Alerta: A Blockchain foi violada ou contém blocos inconsistentes!")
    
    st.subheader("Blocos da Blockchain")
    
    # Container com a lista de blocos (mantendo o layout com st.expander)
    blockchain_container = st.container()
    
    with blockchain_container:
        for block in st.session_state.blockchain.blocks:
            with st.expander(f"📦 Bloco #{block.index}", expanded=True):
                st.markdown(f"""
                **Hash Anterior:** `{block.previous_hash}`  
                **Timestamp:** {datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}  
                **Nonce (PoW):** `{block.nonce}`  
                **Hash:** `{block.hash}`  
                **Dados Armazenados:** {block.data}
                """)
