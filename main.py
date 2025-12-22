import os
from flask import Flask, request, jsonify, Response
from openai import OpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import json

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "ft:gpt-4o-mini:personal:trinity_v1:jkl012"  # ← YOUR FINE-TUNE

# Load RAG (once at startup)
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.load_local("data/trinity_rag_index", embeddings)

# Shared Systems (with few-shot examples from datasets)
TRINITY_SYSTEM = """
You are the Trinity: Abraham (father of faith), Moses (lawgiver), Jesus (Son of grace). 
Respond as a dialogue: Abraham speaks first (archaic), Moses second (prophetic), Jesus last (compassionate/parabolic).
Draw from OT/NT/ANE myths via RAG context. End with unity in God's plan.
Few-shot: Abraham: "I left Ur by promise." Moses: "Thus saith the Lord from Sinai." Jesus: "Verily, love fulfills the law."
"""

ABRAHAM_SYSTEM = "You are Abraham... [from previous]"
MOSES_SYSTEM = "You are Moses... [from previous]"
JESUS_SYSTEM = "You are Jesus... [from previous]"

# RAG Helper
def get_context(query):
    relevant = vectorstore.similarity_search(query, k=3)
    return "\n".join([d.page_content for d in relevant])

@app.route('/trinity', methods=['POST'])  # NEW: Group Chat
def trinity_chat():
    query = request.json.get('query', '')
    context = get_context(query)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"{TRINITY_SYSTEM}\nContext: {context}"},
            {"role": "user", "content": query}
        ],
        max_tokens=400
    )
    return jsonify({"dialogue": response.choices[0].message.content})

@app.route('/abraham', methods=['POST'])
def abraham():
    query = request.json.get('query', '')
    context = get_context(query)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"{ABRAHAM_SYSTEM}\nContext: {context}"},
            {"role": "user", "content": query}
        ],
        max_tokens=300
    )
    text = response.choices[0].message.content
    # TTS (shared)
    speech = client.audio.speech.create(model="tts-1", voice="onyx", input=text)
    return Response(speech.content, mimetype="audio/mpeg")  # Or jsonify for text

# Similar for /moses, /jesus, /speak (English voice), /aramaic, etc. [from previous codes]

@app.route('/chat', methods=['POST'])  # Legacy/Plugin Endpoint
def chat():
    # Default to Trinity
    return trinity_chat()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
