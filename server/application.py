from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os, uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SearchParams, Distance, VectorParams
from fastapi.middleware.cors import CORSMiddleware

client = OpenAI()

QDRANT_HOST = os.environ['QDRANT_HOST']
QDRANT_PORT = os.environ['QDRANT_PORT']
# QDRANT_URL = os.environ['QDRANT_URL_WORKING']

qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
# qdrant_client = QdrantClient(host="localhost", port=6333)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://salmon-moss-08b81541e.5.azurestaticapps.net"],  # Allows access from your React app
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class TextInput(BaseModel):
    text: str
    
@app.post("/api/generate-and-store-embeddings/")
async def generate_embeddings(input: TextInput):
    try:
        print('calling openai')
        # Generate embeddings using OpenAI's API
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=input.text 
        )
        embeddings = response['data'][0]['embedding'] if isinstance(response, dict) else response.data[0].embedding
        print('made it through openai')
        # print('qdrant host:' + QDRANT_HOST)
        # print('qdrant port:' + QDRANT_PORT)
        # print('qdrant URL:' + QDRANT_URL)
        print(embeddings)
        vector_id = str(uuid.uuid4())
        
      # Assuming qdrant_client has been initialized
        try:
            # Attempt to check if the collection exists
            collection_exists = qdrant_client.collection_exists(collection_name="example_collection")
        except Exception as e:
            # Handle all exceptions that could be thrown by the collection_exists method
            if '404' in str(e):  # Assuming the error message contains the status code
                collection_exists = False
                print('The collection does not exist, will attempt to create it.')
            else:
                # Log unexpected exceptions and re-raise them
                print(f"An unexpected error occurred: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        if not collection_exists:
            print('Collection does not exist, creating it...')
            try:
                qdrant_client.create_collection(
                    collection_name="example_collection",
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
            except Exception as e:
                # Handle exceptions that might occur during collection creation
                print(f"Failed to create collection: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Prepare a point for Qdrant insertion
        point = PointStruct(
            id=vector_id,
            vector=embeddings,
            payload={"text": input.text},
        )

        # Insert the point into Qdrant
        print('inserting into collection')
        qdrant_client.upsert(collection_name="example_collection", points=[point])
        return {"message": "Embeddings generated and stored successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@app.post("/api/retrieve-and-generate-response")
async def retrieve_and_generate_response(input: TextInput):
    print('Made it here into the route')
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