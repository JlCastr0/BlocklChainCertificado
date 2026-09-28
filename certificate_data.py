import json
from datetime import datetime

class CertificateData:
    def __init__(self, cert_id, student_id, student_name, course, document_hash, issue_date=None, issuer="secretaria_uea", status="ATIVO"):
        """
        Representa os dados de um certificado acadêmico armazenado na Blockchain.
        :param cert_id: Código único de registro do certificado (ex: CERT-2026-01)
        :param student_id: Matrícula do aluno
        :param student_name: Nome completo do aluno
        :param course: Nome do curso ou evento acadêmico
        :param document_hash: Hash SHA-256 do arquivo original (PDF/Imagem)
        :param issue_date: Data e hora da emissão
        :param issuer: Identificador da entidade emissora (ex: secretaria_uea)
        :param status: Estado atual do certificado (ATIVO ou REVOGADO)
        """
        self.cert_id = cert_id
        self.student_id = student_id
        self.student_name = student_name
        self.course = course
        self.document_hash = document_hash
        self.issue_date = issue_date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.issuer = issuer
        self.status = status

    def to_dict(self):
        return {
            'cert_id': self.cert_id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'course': self.course,
            'document_hash': self.document_hash,
            'issue_date': self.issue_date,
            'issuer': self.issuer,
            'status': self.status
        }

    def to_json(self):
        """
        Converte os dados do certificado para JSON formatado
        """
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_str):
        """
        Recria uma instância de CertificateData a partir de string JSON
        """
        data = json.loads(json_str)
        return CertificateData(
            cert_id=data.get('cert_id'),
            student_id=data.get('student_id'),
            student_name=data.get('student_name'),
            course=data.get('course'),
            document_hash=data.get('document_hash'),
            issue_date=data.get('issue_date'),
            issuer=data.get('issuer', 'secretaria_uea'),
            status=data.get('status', 'ATIVO')
        )

    def __str__(self):
        return f"Certificado [{self.cert_id}] - Aluno: {self.student_name} ({self.student_id}) - Curso: {self.course} - Status: {self.status} - Hash Doc: {self.document_hash[:16]}..."
