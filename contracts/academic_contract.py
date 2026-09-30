# contracts/academic_contract.py
from datetime import datetime
from core.certificate_data import CertificateData


class AcademicSmartContract:
    """
    Smart Contract (Contrato Inteligente) que implementa as regras de negócio
    para emissão, validação, consulta e revogação de certificados acadêmicos.
    """

    def __init__(self, admin_role="secretaria_uea"):
        self.admin = admin_role
        self.authorized_issuers = {admin_role}

        # Estado do contrato:
        # Mapeamento: document_hash -> dados do certificado
        self.certificates = {}
        # Mapeamento auxiliar: cert_id -> document_hash
        self.cert_id_index = {}

    def is_authorized(self, caller_role):
        """Verifica se o chamador possui permissão de emissor autorizado."""
        return caller_role in self.authorized_issuers

    def issue_certificate(self, caller_role, cert: CertificateData):
        """
        Regra de Negócio 1: Emissão de Certificado.
        - Valida permissão do emissor
        - Valida preenchimento dos campos obrigatórios
        - Valida unicidade (impede duplicidade de hash e código)
        """
        # Verificação de Permissão (Controle de Acesso)
        if not self.is_authorized(caller_role):
            raise PermissionError(
                f"[Acesso Negado] O perfil '{caller_role}' não tem permissão para emitir "
                "certificados. Apenas emissores autorizados (Secretaria)."
            )

        # Validação de Dados Obrigatórios
        if not cert.cert_id or not cert.cert_id.strip():
            raise ValueError("[Operação Inválida] O código do certificado (cert_id) é obrigatório.")
        if not cert.student_id or not cert.student_id.strip():
            raise ValueError("[Operação Inválida] A matrícula do aluno (student_id) é obrigatória.")
        if not cert.student_name or not cert.student_name.strip():
            raise ValueError("[Operação Inválida] O nome do aluno é obrigatório.")
        if not cert.course or not cert.course.strip():
            raise ValueError("[Operação Inválida] O curso é obrigatório.")
        if not cert.document_hash or len(cert.document_hash) != 64:
            raise ValueError("[Operação Inválida] Hash SHA-256 do documento inválido ou ausente.")

        # Validação de Unicidade (Anti-duplicidade)
        if cert.document_hash in self.certificates:
            existing = self.certificates[cert.document_hash]
            raise ValueError(
                f"[Operação Inválida] Este documento já foi registrado anteriormente "
                f"com o código '{existing['cert_id']}'."
            )

        if cert.cert_id in self.cert_id_index:
            raise ValueError(
                f"[Operação Inválida] O código de certificado '{cert.cert_id}' já foi utilizado."
            )

        # Atualização do Estado do Contrato
        cert.issuer = caller_role
        cert.status = "ATIVO"
        self.certificates[cert.document_hash] = cert.to_dict()
        self.cert_id_index[cert.cert_id] = cert.document_hash

        return True, "Certificado validado e emitido pelo contrato com sucesso."

    def revoke_certificate(self, caller_role, cert_id_or_hash, reason="Irregularidade ou cancelamento acadêmico"):
        """
        Regra de Negócio 2: Revogação de Certificado.
        - Valida permissão do emissor
        - Altera o estado do certificado para 'REVOGADO' sem apagar da blockchain
        """
        if not self.is_authorized(caller_role):
            raise PermissionError(
                f"[Acesso Negado] O perfil '{caller_role}' não tem permissão para revogar certificados."
            )

        # Localiza o certificado por código ou por hash
        doc_hash = self.cert_id_index.get(cert_id_or_hash, cert_id_or_hash)

        if doc_hash not in self.certificates:
            raise KeyError(
                f"[Operação Inválida] Certificado '{cert_id_or_hash}' não encontrado no contrato."
            )

        cert_data = self.certificates[doc_hash]

        if cert_data['status'] == "REVOGADO":
            raise ValueError(
                f"[Operação Inválida] O certificado '{cert_data['cert_id']}' já se encontra revogado."
            )

        # Altera estado no contrato
        cert_data['status'] = "REVOGADO"
        cert_data['revocation_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cert_data['revocation_reason'] = reason

        revoked_cert = CertificateData(
            cert_id=cert_data['cert_id'],
            student_id=cert_data['student_id'],
            student_name=cert_data['student_name'],
            course=cert_data['course'],
            document_hash=cert_data['document_hash'],
            issue_date=cert_data.get('revocation_date'),
            issuer=caller_role,
            status="REVOGADO"
        )

        return revoked_cert, f"Certificado '{cert_data['cert_id']}' foi revogado com sucesso. Motivo: {reason}"

    def verify_certificate(self, document_hash=None, cert_id=None):
        """
        Regra de Negócio 3: Consulta e Validação de Autenticidade.
        Retorna as informações do contrato se o certificado for autêntico.
        """
        doc_hash = None
        if cert_id and cert_id in self.cert_id_index:
            doc_hash = self.cert_id_index[cert_id]
        elif document_hash and document_hash in self.certificates:
            doc_hash = document_hash

        if not doc_hash or doc_hash not in self.certificates:
            return {
                "valid": False,
                "status": "INEXISTENTE",
                "message": "Certificado não encontrado na base da Blockchain. Documento não autêntico ou não registrado."
            }

        cert_info = self.certificates[doc_hash]
        is_active = cert_info.get('status') == "ATIVO"

        return {
            "valid": is_active,
            "status": cert_info.get('status'),
            "data": cert_info,
            "message": (
                "Certificado Válido e Ativo"
                if is_active
                else f"Certificado INVÁLIDO/REVOGADO! Motivo: {cert_info.get('revocation_reason', 'Não informado')}"
            )
        }
