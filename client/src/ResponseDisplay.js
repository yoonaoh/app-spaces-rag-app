import React from 'react';

function ResponseDisplay({ response }) {
  return (
    <div>
      <h2>Response</h2>
      <p>{response || 'No response received. Please try another query.'}</p>
    </div>
  );
}

export default ResponseDisplay;
