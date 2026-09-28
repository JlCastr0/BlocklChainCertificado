from flask import Flask, render_template, request, jsonify
from blockchain import Blockchain
from certificate_data import CertificateData
from smart_contract import AcademicSmartContract
import hashlib
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializar blockchain e contrato
blockchain = Blockchain(difficulty=3)
contract = AcademicSmartContract(admin_role="secretaria_uea")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_file_data(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

@app.route('/')
def index():
    return jsonify({
        'system': 'Blockchain de Certificados Acadêmicos - UEA',
        'status': 'online',
        'endpoints': {
            'POST /issue': 'Emissão de certificado (requer permissão de secretaria)',
            'POST /revoke': 'Revogação de certificado (requer permissão de secretaria)',
            'GET /verify': 'Consulta e validação de autenticidade (?cert_id=... ou ?hash=...)',
            'GET /blockchain': 'Visualização de todos os blocos e integridade'
        }
    })

@app.route('/issue', methods=['POST'])
def issue_certificate():
    caller_role = request.form.get('caller_role', 'secretaria_uea')
    cert_id = request.form.get('cert_id', '')
    student_id = request.form.get('student_id', '')
    student_name = request.form.get('student_name', '')
    course = request.form.get('course', '')
    
    if 'document' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['document']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Arquivo inválido ou extensão não permitida'}), 400

    try:
        doc_hash = hash_file_data(file.read())
        cert_data = CertificateData(
            cert_id=cert_id,
            student_id=student_id,
            student_name=student_name,
            course=course,
            document_hash=doc_hash,
            issuer=caller_role
        )
        
        # Validação pelo Smart Contract
        contract.issue_certificate(caller_role, cert_data)
        
        # Mineração na Blockchain
        new_block = blockchain.new_block(cert_data)
        blockchain.add_block(new_block)
        
        return jsonify({
            'success': True,
            'message': 'Certificado emitido e gravado na Blockchain',
            'block_index': new_block.index,
            'block_hash': new_block.hash,
            'document_hash': doc_hash
        })
    except PermissionError as e:
        return jsonify({'error': 'Rejeição de Permissão', 'detail': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': 'Rejeição de Validação', 'detail': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/revoke', methods=['POST'])
def revoke_certificate():
    caller_role = request.form.get('caller_role', 'secretaria_uea')
    cert_id = request.form.get('cert_id', '')
    reason = request.form.get('reason', 'Irregularidade detectada')
    
    try:
        revoked_cert, msg = contract.revoke_certificate(caller_role, cert_id, reason)
        rev_block = blockchain.new_block(revoked_cert)
        blockchain.add_block(rev_block)
        return jsonify({
            'success': True,
            'message': msg,
            'block_index': rev_block.index,
            'block_hash': rev_block.hash
        })
    except PermissionError as e:
        return jsonify({'error': 'Rejeição de Permissão', 'detail': str(e)}), 403
    except (ValueError, KeyError) as e:
        return jsonify({'error': 'Operação Inválida', 'detail': str(e)}), 400

@app.route('/verify', methods=['GET'])
def verify():
    cert_id = request.args.get('cert_id')
    doc_hash = request.args.get('hash')
    result = contract.verify_certificate(document_hash=doc_hash, cert_id=cert_id)
    return jsonify(result)

@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    return jsonify({
        'blocks': [str(block) for block in blockchain.blocks],
        'total_blocks': len(blockchain.blocks),
        'is_valid': blockchain.is_blockchain_valid()
    })

if __name__ == '__main__':
    app.run(debug=True)
