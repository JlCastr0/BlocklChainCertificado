import unittest
import hashlib
from blockchain import Blockchain
from certificate_data import CertificateData
from smart_contract import AcademicSmartContract

class TestAcademicBlockchainContract(unittest.TestCase):
    def setUp(self):
        self.contract = AcademicSmartContract(admin_role="secretaria_uea")
        self.blockchain = Blockchain(difficulty=2)
        
        # Dados de exemplo
        self.dummy_pdf_bytes = b"%PDF-1.4 Mock de Diploma da Universidade do Estado do Amazonas (UEA)"
        self.doc_hash = hashlib.sha256(self.dummy_pdf_bytes).hexdigest()
        
        self.valid_cert = CertificateData(
            cert_id="UEA-2026-ENG-001",
            student_id="202108001",
            student_name="Carlos Drummond de Andrade",
            course="Engenharia de Software",
            document_hash=self.doc_hash,
            issuer="secretaria_uea"
        )

    def test_01_valid_issuance(self):
        """Teste 1: Emissão válida por autoridade competente (Secretaria)"""
        success, msg = self.contract.issue_certificate("secretaria_uea", self.valid_cert)
        self.assertTrue(success)
        
        # Registra na Blockchain
        block = self.blockchain.new_block(self.valid_cert)
        self.blockchain.add_block(block)
        
        # Verifica se o bloco foi inserido e a blockchain continua íntegra
        self.assertEqual(len(self.blockchain.blocks), 2) # Gênesis + Bloco 1
        self.assertTrue(self.blockchain.is_blockchain_valid())

    def test_02_rejection_unauthorized_issuer(self):
        """Teste 2: Rejeição de operação sem permissão (Aluno tentando emitir certificado)"""
        with self.assertRaises(PermissionError) as context:
            self.contract.issue_certificate("aluno_publico", self.valid_cert)
        
        self.assertIn("não tem permissão", str(context.exception))
        # Garante que nenhum bloco foi adicionado
        self.assertEqual(len(self.blockchain.blocks), 1)

    def test_03_rejection_duplicate_document(self):
        """Teste 3: Rejeição de operação inválida (Duplicidade de documento/hash)"""
        # Primeira emissão: OK
        self.contract.issue_certificate("secretaria_uea", self.valid_cert)
        
        # Segunda emissão com mesmo hash de documento
        cert_duplicado = CertificateData(
            cert_id="UEA-2026-ENG-002",
            student_id="202108002",
            student_name="Outro Aluno",
            course="Engenharia",
            document_hash=self.doc_hash, # Mesmo hash
            issuer="secretaria_uea"
        )
        
        with self.assertRaises(ValueError) as context:
            self.contract.issue_certificate("secretaria_uea", cert_duplicado)
        
        self.assertIn("já foi registrado anteriormente", str(context.exception))

    def test_04_verification_authentic_and_tampered(self):
        """Teste 4: Consulta e verificação (Documento autêntico vs Adulterado)"""
        self.contract.issue_certificate("secretaria_uea", self.valid_cert)
        
        # Consulta com o hash correto
        result_ok = self.contract.verify_certificate(document_hash=self.doc_hash)
        self.assertTrue(result_ok["valid"])
        self.assertEqual(result_ok["status"], "ATIVO")
        self.assertEqual(result_ok["data"]["student_name"], "Carlos Drummond de Andrade")
        
        # Consulta com arquivo adulterado (hash diferente)
        tampered_hash = hashlib.sha256(b"Documento adulterado com alteracao de nota").hexdigest()
        result_fail = self.contract.verify_certificate(document_hash=tampered_hash)
        self.assertFalse(result_fail["valid"])
        self.assertEqual(result_fail["status"], "INEXISTENTE")

    def test_05_state_transition_revocation(self):
        """Teste 5: Alteração de estado no contrato (Revogação de certificado)"""
        self.contract.issue_certificate("secretaria_uea", self.valid_cert)
        
        # Aluno não pode revogar
        with self.assertRaises(PermissionError):
            self.contract.revoke_certificate("aluno_publico", self.valid_cert.cert_id)
            
        # Secretaria revoga
        revoked_cert, msg = self.contract.revoke_certificate(
            caller_role="secretaria_uea",
            cert_id_or_hash=self.valid_cert.cert_id,
            reason="Cancelamento de matrícula por fraude documental"
        )
        self.assertEqual(revoked_cert.status, "REVOGADO")
        
        # Grava a revogação na blockchain
        rev_block = self.blockchain.new_block(revoked_cert)
        self.blockchain.add_block(rev_block)
        self.assertTrue(self.blockchain.is_blockchain_valid())
        
        # Consulta o estado atualizado
        result_rev = self.contract.verify_certificate(cert_id=self.valid_cert.cert_id)
        self.assertFalse(result_rev["valid"])
        self.assertEqual(result_rev["status"], "REVOGADO")
        self.assertIn("Cancelamento de matrícula", result_rev["message"])

    def test_06_blockchain_tamper_detection(self):
        """Teste 6: Detecção de adulteração direta em bloco da Blockchain"""
        self.contract.issue_certificate("secretaria_uea", self.valid_cert)
        block = self.blockchain.new_block(self.valid_cert)
        self.blockchain.add_block(block)
        
        self.assertTrue(self.blockchain.is_blockchain_valid())
        
        # Tentativa maliciosa de adulterar os dados de um bloco minerado
        self.blockchain.blocks[1].data = "Dados adulterados por invasor"
        
        # A validação da Blockchain deve detectar a quebra criptográfica
        self.assertFalse(self.blockchain.is_blockchain_valid())

if __name__ == "__main__":
    unittest.main()
