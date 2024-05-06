import React, { useState } from 'react';
import InputForm from './InputForm';
import StoreInputForm from './StoreInputForm';
import DocumentsDisplay from './DocumentsDisplay';
import ResponseDisplay from './ResponseDisplay';
import axios from 'axios';
import './App.css';

function App() {
  const [response, setResponse] = useState('Enter a statement or a question below to get started');
  const [documents, setDocuments] = useState([]);
  const [storeStatus, setStoreStatus] = useState('');

  const handleSearchSubmit = async (text) => {
    try {
      const result = await axios.post('http://localhost:8000/retrieve-and-generate-response/', { text });
      setResponse(result.data.response);
      setDocuments(result.data.documents);
    } catch (error) {
      console.error('Error fetching data: ', error);
      setResponse('Failed to fetch data');
    }
  };

  const handleStoreSubmit = async (text) => {
    try {
      const result = await axios.post('http://localhost:8000/generate-and-store-embeddings/', { text });
      setStoreStatus(result.data.message);
    } catch (error) {
      console.error('Error storing data: ', error);
      setStoreStatus('Failed to store data');
    }
  };

  return (
    <div>
      <h1>Retrieval-Augmented Generation Basic App</h1>
      <div className="app-container">
        <ResponseDisplay response={response} />
        <DocumentsDisplay documents={documents} />
        <InputForm onSubmit={handleSearchSubmit} placeholder="Enter your question here" />
        <StoreInputForm onSubmit={handleStoreSubmit} placeholder="Enter text to store in DB" />
        <div>{storeStatus}</div>
      </div>
    </div>
  );
}

export default App;
