from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os, uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SearchParams, Distance
from fastapi.middleware.cors import CORSMiddleware

client = OpenAI()
qdrant_client = QdrantClient(host="localhost", port=6333)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows access from your React app
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class TextInput(BaseModel):
    text: str

@app.post("/api/search")
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
            query_vector=embeddings,
            limit=3
        )
        documents = [{"text": doc.payload['text'], "score": doc.score} for doc in search_result] if search_result else []

        if search_result:
            return {"message": "Embeddings found in Qdrant", "documents": documents}
        else:
            return {"message": "Embeddings not found in Qdrant", "documents": []}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/api/generate-and-store-embeddings/")
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
    
    
@app.post("/api/retrieve-and-generate-response")
async def retrieve_and_generate_response(input: TextInput):
    try:
        print("Retrieving embeddings for the input text")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=input.text 
        )
        embeddings = response['data'][0]['embedding'] if isinstance(response, dict) else response.data[0].embedding

        # Search for the embeddings in Qdrant
        search_result = qdrant_client.search(
            collection_name="example_collection",
            query_vector=embeddings,
            limit=3
        )
        documents = [{"text": doc.payload['text'], "score": doc.score} for doc in search_result] if search_result else []

        
        prompt = f"Question: {input.text}\n\n" + "\n\n".join([f"Document {i+1}: {doc['text']}" for i, doc in enumerate(documents)])
        print(prompt)
        completion = client.chat.completions.create(
         model="gpt-4-turbo",
         messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
  ]
)
        return {"response": completion.choices[0].message.content, "documents": documents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
#         print("Generating response using GPT-4")
#         completion = client.chat.completions.create(
#          model="gpt-4-turbo",
#          messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": prompt}
#   ]
# )
#         # Return the GPT-4 response along with the documents
#         return {"response": completion.choices[0].message.content, "documents": documents}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
