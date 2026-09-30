# main.py
# Demonstração em linha de comando da Blockchain de Certificados com Smart Contract
import hashlib
from core.blockchain import Blockchain
from core.certificate_data import CertificateData
from contracts.academic_contract import AcademicSmartContract


def main():
    print("=" * 65)
    print("  SISTEMA DE CERTIFICADOS ACADÊMICOS — SMART CONTRACT & BLOCKCHAIN")
    print("=" * 65)

    # 1. Inicializa Blockchain e Smart Contract
    difficulty = 3
    blockchain = Blockchain(difficulty)
    contract = AcademicSmartContract(admin_role="secretaria_uea")
    print(f"\n[1] Blockchain inicializada com sucesso (Dificuldade PoW: {difficulty}).")
    print(f"    Bloco Gênesis criado: {blockchain.blocks[0].hash}")

    # 2. Operação Válida: Emissão de Certificado pela Secretaria
    print("\n[2] OPERAÇÃO VÁLIDA: Secretaria emitindo certificado...")
    doc_bytes = b"Diploma de Conclusao de Curso - Engenharia de Software - Aluno: Joao Silva"
    doc_hash = hashlib.sha256(doc_bytes).hexdigest()

    cert1 = CertificateData(
        cert_id="UEA-2026-ENG-001",
        student_id="2021001",
        student_name="João Silva",
        course="Engenharia de Software",
        document_hash=doc_hash,
        issuer="secretaria_uea"
    )

    try:
        contract.issue_certificate("secretaria_uea", cert1)
        new_block = blockchain.new_block(cert1)
        blockchain.add_block(new_block)
        print(f"    ✅ Sucesso! Bloco #{new_block.index} minerado.")
        print(f"    Hash do Bloco: {new_block.hash}")
    except Exception as e:
        print(f"    ❌ Erro: {e}")

    # 3. Operação Inválida: Usuário sem permissão tenta emitir
    print("\n[3] OPERAÇÃO INVÁLIDA (Sem Permissão): Aluno tentando emitir...")
    try:
        cert_fake = CertificateData(
            cert_id="UEA-FAKE-001",
            student_id="2021002",
            student_name="Aluno Falso",
            course="Medicina",
            document_hash=hashlib.sha256(b"fake").hexdigest(),
            issuer="aluno_publico"
        )
        contract.issue_certificate("aluno_publico", cert_fake)
    except PermissionError as e:
        print(f"    🛑 REJEIÇÃO CONFIRMADA PELO CONTRATO: {e}")

    # 4. Operação Inválida: Duplicidade de certificado
    print("\n[4] OPERAÇÃO INVÁLIDA (Duplicidade): Reemitir mesmo documento...")
    try:
        contract.issue_certificate("secretaria_uea", cert1)
    except ValueError as e:
        print(f"    🛑 REJEIÇÃO CONFIRMADA PELO CONTRATO: {e}")

    # 5. Consulta e Alteração de Estado (Revogação)
    print("\n[5] ALTERAÇÃO DE ESTADO: Revogando certificado por irregularidade...")
    revoked_cert, msg = contract.revoke_certificate(
        caller_role="secretaria_uea",
        cert_id_or_hash="UEA-2026-ENG-001",
        reason="Documentação adulterada detectada na auditoria"
    )
    rev_block = blockchain.new_block(revoked_cert)
    blockchain.add_block(rev_block)
    print(f"    ⚠️  {msg}")
    print(f"    Alteração gravada no Bloco #{rev_block.index}. Hash: {rev_block.hash}")

    # 6. Consulta do estado atual
    status_query = contract.verify_certificate(cert_id="UEA-2026-ENG-001")
    print(f"\n[6] Consulta final do certificado: Status = {status_query['status']}")
    print(f"    Mensagem do Contrato: {status_query['message']}")

    # 7. Integridade da Blockchain
    print("\n[7] Verificando integridade da Blockchain...")
    print("    A Blockchain é válida?", "SIM ✅" if blockchain.is_blockchain_valid() else "NÃO ❌")
    print(f"    Total de blocos: {len(blockchain.blocks)}")
    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
