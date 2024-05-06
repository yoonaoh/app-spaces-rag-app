import React, { useState } from 'react';

function StoreInputForm({ onSubmit, placeholder }) {
  const [text, setText] = useState('');

  const handleInputChange = (e) => {
    setText(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(text);
    setText(''); // Clear the input after submission
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" value={text} onChange={handleInputChange} placeholder={placeholder} />
      <button type="submit">Store Text</button>
    </form>
  );
}

export default StoreInputForm;
