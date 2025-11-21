import os
from flask import Flask, request, jsonify
from google import genai
from google.genai.errors import APIError
from flask_cors import CORS

# --- Configuração Inicial ---
app = Flask(__name__)
CORS(app)

# --- Memória da Conversa (Para a IA não esquecer o contexto) ---
conversation_history = []

# --- Configuração da IA ---
try:
    # O cliente pega a chave automaticamente do comando 'set GEMINI_API_KEY=...'
    client = genai.Client(api_key="AIzaSyBzYtwkDBYW5u3585iTvkP8wYHVWHzM_uo")
    MODEL = 'gemini-2.5-flash'
    print("✅ IA Gemini inicializada com sucesso.")
except Exception as e:
    print(f"⚠️ Erro ao inicializar Gemini: {e}")
    client = None

def get_ai_response(prompt_aluno):
    global conversation_history
    
    # Instrução para a IA agir como um tutor humano
    system_instruction = (
        "Você é um tutor de Ciências experiente e amigável. "
        "Responda de forma conversacional, como um ser humano falaria. "
        "Seja breve e direto para que a conversa por voz flua bem. "
        "Use o histórico da conversa para manter o contexto."
    )
    
    if not client:
        return "Erro: IA não configurada. Verifique a chave no CMD."

    try:
        # 1. Adiciona o que o aluno disse ao histórico
        conversation_history.append(f"Aluno: {prompt_aluno}")
        
        # 2. Cria um contexto com as últimas 10 trocas de mensagem
        contexto_completo = "\n".join(conversation_history[-10:])
        
        # 3. Envia tudo para a IA
        response = client.models.generate_content(
            model=MODEL,
            contents=[contexto_completo],
            config={"system_instruction": system_instruction}
        )
        
        resposta_texto = response.text
        
        # 4. Guarda a resposta da IA no histórico
        conversation_history.append(f"Tutor: {resposta_texto}")
        
        return resposta_texto
        
    except Exception as e:
        return f"Erro interno na IA: {e}"

def generate_quiz_question(topic):
    """Gera uma pergunta de quiz formatada"""
    prompt = f"Crie uma pergunta de múltipla escolha (A, B, C, D) sobre: {topic}. Formato: [PERGUNTA] [OPÇÕES] [RESPOSTA CORRETA]"
    try:
        if not client: return "Erro: IA offline."
        response = client.models.generate_content(model=MODEL, contents=[prompt])
        return response.text
    except Exception as e:
        return f"Erro no quiz: {e}"

# --- Rotas do Servidor ---

@app.route('/ask_tutor', methods=['POST'])
def ask_tutor():
    data = request.get_json()
    pergunta = data.get('pergunta', '')
    if not pergunta: return jsonify({"resposta": "Não entendi..."}), 400
    
    resposta = get_ai_response(pergunta)
    return jsonify({"resposta": resposta})

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    topic = data.get('topico', '')
    if not topic: return jsonify({"quiz": "Preciso de um tópico."}), 400
    
    quiz = generate_quiz_question(topic)
    return jsonify({"quiz": quiz})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
