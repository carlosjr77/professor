import os
from flask import Flask, request, jsonify
from google import genai
from google.genai.errors import APIError
from flask_cors import CORS

# --- Configuração Inicial ---
app = Flask(__name__)
# Permite que o frontend do GitHub Pages se comunique com o backend do Render
CORS(app)

# --- Memória da Conversa (Para a IA não esquecer o contexto) ---
# Nota: Em produção real, você usaria um banco de dados para salvar a conversa de cada usuário.
conversation_history = []

# --- Configuração da IA ---
try:
    # IMPORTANTE: genai.Client() buscará a chave automaticamente da variável de ambiente
    # GEMINI_API_KEY que você definiu no Render. A chave não está mais no código!
    client = genai.Client()
    MODEL = "gemini-2.5-flash"
    
    if client:
        print('✅ IA Gemini inicializada com sucesso.')
    else:
        print('⚠️ Falha ao criar cliente GenAI.')

except Exception as e:
    # Capturar erros na inicialização
    print(f"❌ Erro ao inicializar Gemini: {e}")
    client = None
    
# --- Rota Principal para Conversa ---
@app.route('/ask_tutor', methods=['POST'])
def get_ai_response():
    global conversation_history
    
    # 1. Checagem de Conexão
    if not client:
        return jsonify({"error": "Erro: IA não configurada. Verifique a chave de API."}), 500

    try:
        data = request.get_json()
        prompt_aluno = data.get('prompt')

        if not prompt_aluno:
            return jsonify({"error": "Nenhum prompt fornecido."}), 400

        # --- Instrução para a IA agir como um tutor humano ---
        system_instruction = (
            "Você é um tutor de Ciências experiente e amigável."
            "Responda de forma conversacional, como um ser humano falaria."
            "Seja breve e direto para que a conversa flua bem."
            "Use o histórico da conversa para manter o contexto."
        )

        # 1. Adiciona o que o aluno disse ao histórico
        conversation_history.append({'role': 'user', 'parts': [{'text': prompt_aluno}]})

        # 2. Gera a resposta da IA
        response = client.models.generate_content(
            model=MODEL,
            contents=conversation_history,
            config={"system_instruction": system_instruction}
        )

        # 3. Adiciona a resposta da IA ao histórico
        ai_response_text = response.text
        conversation_history.append({'role': 'model', 'parts': [{'text': ai_response_text}]})

        # 4. Retorna a resposta
        return jsonify({"response": ai_response_text})

    except APIError as e:
        print(f"❌ Erro na API de IA: {e}")
        return jsonify({"error": f"Erro na API de IA: Ocorreu um problema ao gerar a resposta. ({e})", "details": str(e)}), 500
    
    except Exception as e:
        print(f"❌ Erro interno: {e}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

# --- Rota para Limpar Histórico ---
@app.route('/clear_history', methods=['POST'])
def clear_history():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "Histórico de conversa limpo com sucesso."})

# --- Rota para Geração de Quiz (Exemplo) ---
@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    return jsonify({"quiz_status": "Funcionalidade de Quiz ativada e pronta para ser desenvolvida."})

# NOTE: O BLOCO if __name__ == '__main__': FOI REMOVIDO, POIS O RENDER USA O GUNICORN.
