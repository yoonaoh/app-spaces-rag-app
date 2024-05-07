import React, { useState } from 'react';
import InputForm from './InputForm';
import StoreInputForm from './StoreInputForm';
import DocumentsDisplay from './DocumentsDisplay';
import ResponseDisplay from './ResponseDisplay';
import axios from 'axios';
import './App.css';

function App() {
  const [response, setResponse] = useState('');
  const [documents, setDocuments] = useState([]);
  const [storeStatus, setStoreStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSearchSubmit = async (text) => {
    setIsLoading(true);
    try {
      const result = await axios.post('http://localhost:8000/retrieve-and-generate-response/', { text });
      setResponse(result.data.response);
      setDocuments(result.data.documents);
    } catch (error) {
      console.error('Error fetching data: ', error);
      setResponse('Failed to fetch data');
    }
    setIsLoading(false);
  };

  const handleStoreSubmit = async (text) => {
    // setIsLoading(true);
    try {
      const result = await axios.post('http://localhost:8000/generate-and-store-embeddings/', { text });
      setStoreStatus(result.data.message);
    } catch (error) {
      console.error('Error storing data: ', error);
      setStoreStatus('Failed to store data');
    }
    // setIsLoading(false);
  };
  return (
    <div className="app container mt-5">
      <h1 className="text-center mb-4">Retrieval-Augmented Generation Basic App</h1>
      
      <div className="search-section card mb-4">
        <div className="card-body">
          <h2 className="card-title">Ask a question</h2>
          <p className="card-text">After you've stored documents in the vector database, you can use the input box below to search the vector database for stored text strings/documents. The text you search for will be sent to OpenAI to generate embeddings, and those embeddings will be used during the retrieval process to surface information relating to your search query.</p>
          <InputForm onSubmit={handleSearchSubmit} placeholder="Enter your question here" />
          {isLoading ? (
            <div className="text-center">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : (
            <>
              <ResponseDisplay response={response} />
              <DocumentsDisplay documents={documents} />
            </>
          )}
        </div>
      </div>
      
      <div className="store-section card">
        <div className="card-body">
          <h2 className="card-title">Store new text</h2>
          <p className="card-text">You can use the input box below to store new data inside the vector database. The text you input will first be sent to the OpenAI API to generate embeddings, and then those embeddings will be stored in a Qdrant vector database.</p>
          <StoreInputForm onSubmit={handleStoreSubmit} placeholder="Enter text to store in DB" />
          <div className="status mt-3">{storeStatus}</div>
        </div>
      </div>
    </div>
  );
}

export default App;
