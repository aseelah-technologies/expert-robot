from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List

class MistralHandler:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
        self.model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-Instruct-v0.1",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True
        )
        
        if torch.cuda.is_available():
            self.model = self.model.cuda()
        
        self.model.eval()

    def generate_response(self, question: str, context: List[str]) -> str:
        # Combine context and question
        prompt = f"""Context: {' '.join(context)}

Question: {question}

Please provide a response based only on the context provided above."""

        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=512,
                temperature=0.7,
                num_return_sequences=1
            )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.split("Answer:")[-1].strip()

### 2. Chat Endpoint
Update app/main.py:
```python
from app.utils.mistral_handler import MistralHandler
import numpy as np

mistral = MistralHandler(os.getenv("MODEL_PATH"))

@app.post("/chat")
async def chat(
    message: str,
    current_user: str = Depends(auth_handler.verify_token),
    db: Session = Depends(get_db)
):
    # Get relevant chunks
    query_embedding = DocumentProcessor.create_embeddings(message)
    
    # Get all chunk embeddings from database
    chunks = db.query(DocumentChunk).all()
    chunk_embeddings = [np.array(json.loads(chunk.embedding)) for chunk in chunks]
    
    # Calculate similarities
    similarities = [
        np.dot(query_embedding, chunk_emb) / 
        (np.linalg.norm(query_embedding) * np.linalg.norm(chunk_emb))
        for chunk_emb in chunk_embeddings
    ]
    
    # Get top 3 most relevant chunks
    top_indices = np.argsort(similarities)[-3:]
    relevant_chunks = [chunks[i].content for i in top_indices]
    
    # Generate response using Mistral
    response = mistral.generate_response(message, relevant_chunks)
    
    return {"response": response}