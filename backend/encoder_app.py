from fastapi import FastAPI, Body
from pydantic import BaseModel
import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer
from typing import Dict
import os

app = FastAPI()

# Model for SPLADE
# Using a Japanese-optimized SPLADE model for better Scrapbox search results
MODEL_ID = "hotchpotch/japanese-splade-v2"

device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForMaskedLM.from_pretrained(MODEL_ID).to(device)

class EncodeRequest(BaseModel):
    text: str

@app.post("/encode")
async def encode(request: EncodeRequest):
    tokens = tokenizer(request.text, return_tensors="pt").to(device)
    
    with torch.no_grad():
        output = model(**tokens)
    
    # SPLADE logic: max-pooling over log(1 + ReLU(logits))
    logits = output.logits
    weights = torch.log(1 + torch.relu(logits))
    weights = torch.max(weights, dim=1).values.squeeze()
    
    # Filter non-zero weights
    cols = weights.nonzero().squeeze().cpu().tolist()
    if isinstance(cols, int): cols = [cols]
    
    weights = weights.cpu().tolist()
    
    # Map token IDs to strings for better readability/debugging if needed,
    # or just keep as IDs. Elasticsearch rank_features needs string keys.
    result = {str(i): weights[i] for i in cols if weights[i] > 0.01}
    
    return {"vector": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
