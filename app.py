from flask import Flask, render_template, request, jsonify, redirect
import requests
import os

app = Flask(__name__)

# URL da API (configure no Render)
API_URL = os.environ.get('API_URL', 'https://sakiurl-api.onrender.com')

@app.route('/')
def index():
    return render_template('index.html', api_url=API_URL)

@app.route('/shorten', methods=['POST'])
def shorten_url_frontend():
    """Endpoint do frontend que chama a API"""
    try:
        data = request.json
        
        # Validação básica
        if not data or 'url' not in data:
            return jsonify({'error': 'URL é obrigatória'}), 400
            
        response = requests.post(f'{API_URL}/shorten', json=data, timeout=10)
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Erro ao conectar com a API'}), 500
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/stats/<access_code>')
def stats_frontend(access_code):
    """Página de estatísticas"""
    try:
        response = requests.get(f'{API_URL}/stats/{access_code}', timeout=10)
        if response.status_code == 200:
            stats_data = response.json()
            return render_template('stats.html', **stats_data)
        else:
            return render_template('error.html', message='Código de acesso inválido'), 404
    except requests.exceptions.RequestException:
        return render_template('error.html', message='Erro ao carregar estatísticas'), 500

@app.route('/<short_code>')
def redirect_frontend(short_code):
    """Redirecionamento via frontend"""
    try:
        response = requests.get(f'{API_URL}/{short_code}', allow_redirects=False)
        
        if response.status_code in [301, 302, 307, 308]:
            return redirect(response.headers['Location'])
        elif response.status_code == 200:
            # Se retornou conteúdo (provavelmente embed), mostra ele
            return response.text
        else:
            return render_template('error.html', message='URL não encontrada'), 404
            
    except requests.exceptions.RequestException:
        return render_template('error.html', message='Erro ao processar URL'), 500

# Health check para Render
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'sakiurl-web'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
