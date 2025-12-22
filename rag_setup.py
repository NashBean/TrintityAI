# Run once: rag_setup.py (add this file)
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import json

docs = [json.loads(line)["input"] for line in open("trinity_master.jsonl")]
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(docs, embeddings)
vectorstore.save_local("data/trinity_rag_index")