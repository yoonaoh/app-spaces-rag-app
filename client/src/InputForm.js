import React, { useState } from 'react';

function InputForm({ onSubmit }) {
  const [text, setText] = useState('');

  const handleInputChange = (e) => {
    setText(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(text);
    setText('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" value={text} onChange={handleInputChange} placeholder="Enter your text here" />
      <button type="submit">Submit</button>
    </form>
  );
}

export default InputForm;
