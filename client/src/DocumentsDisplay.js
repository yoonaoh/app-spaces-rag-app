import React from 'react';

function DocumentsDisplay({ documents }) {
  return (
    <div>
      <h2>Top Documents</h2>
      <ul>
        {documents.map((doc, index) => (
          <li key={index}>{doc.text} - Score: {doc.score}</li>
        ))}
      </ul>
    </div>
  );
}

export default DocumentsDisplay;
