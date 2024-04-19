from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os, uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SearchParams, Distance

client = OpenAI()
qdrant_client = QdrantClient(host="localhost", port=6333)
app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/search")
async def search_embeddings(input: TextInput):
    try:
        # Generate embeddings using OpenAI's API
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=input.text 
        )
        embeddings = response['data'][0]['embedding'] if isinstance(response, dict) else response.data[0].embedding

        # Search for the embeddings in Qdrant
        search_result = qdrant_client.search(
            collection_name="example_collection",
            query_vector=embeddings,  # Corrected parameter name
            limit=3
        )
        if search_result:
            print(search_result)
            return {"message": "Embeddings found in Qdrant"}
        else:
            return {"message": "Embeddings not found in Qdrant"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/generate-and-store-embeddings/")
async def generate_embeddings(input: TextInput):
    try:
        # Generate embeddings using OpenAI's API
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=input.text 
        )
        embeddings = response['data'][0]['embedding'] if isinstance(response, dict) else response.data[0].embedding
        vector_id = str(uuid.uuid4())
    
        
        # Prepare a point for Qdrant insertion
        point = PointStruct(
            id=vector_id,
            vector=embeddings,
            payload={"text": input.text},
        )

        # Insert the point into Qdrant
        qdrant_client.upsert(collection_name="example_collection", points=[point])
        return {"message": "Embeddings generated and stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
