from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# URL da API (vai ser configurada no Render)
API_URL = os.environ.get('API_URL', 'https://sakiurl-api.onrender.com')

@app.route('/')
def index():
    return render_template('index.html', api_url=API_URL)

@app.route('/shorten', methods=['POST'])
def shorten_url_frontend():
    """Endpoint do frontend que chama a API"""
    try:
        data = request.json
        response = requests.post(f'{API_URL}/shorten', json=data, timeout=10)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Erro ao conectar com o servidor'}), 500

@app.route('/stats/<access_code>')
def stats_frontend(access_code):
    """Página de estatísticas"""
    try:
        response = requests.get(f'{API_URL}/stats/{access_code}', timeout=10)
        if response.status_code == 200:
            stats_data = response.json()
            return render_template('stats.html', **stats_data)
        else:
            return "Código de acesso inválido", 404
    except requests.exceptions.RequestException:
        return "Erro ao carregar estatísticas", 500

@app.route('/<short_code>')
def redirect_frontend(short_code):
    """Redirecionamento via frontend"""
    try:
        response = requests.get(f'{API_URL}/{short_code}', allow_redirects=False)
        
        if response.status_code in [301, 302]:
            return redirect(response.headers['Location'])
        else:
            # Se não é redirecionamento, mostra o conteúdo (embed)
            return response.content, response.status_code
            
    except requests.exceptions.RequestException:
        return "Erro ao processar URL", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)