import React, { useState } from 'react';
import './styles.css';

export default function FormSection() {
  const [age, setAge] = useState('');
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [goal, setGoal] = useState('');

  function handleSubmit(event) {
    event.preventDefault();
    // TODO: implement logic to recommend books based on input
  }

  return (
    <section class = "FormS">
      <h2>Recommend Books</h2>
      <form class="req_btn" onSubmit={handleSubmit}>
        <label className='form_input' >
          Book Title:
          <input className="input" type="number" value={age} onChange={(event) => setAge(event.target.value)} />
        </label>
        <br />
        <label className='form_input' >
          Author:
          <input className="input" type="number" value={weight} onChange={(event) => setWeight(event.target.value)} />
        </label>
        <br />
        <label className='form_input' >
          Genres:
          <input className="input" type="number" value={height} onChange={(event) => setHeight(event.target.value)} />
        </label>
        <br />
        <label className='form_input' >
          Goal:
          <select className="input" value={goal} onChange={(event) => setGoal(event.target.value)}>
            <option value="">Recommend by Similar Books</option>
            <option value="lose">Recommend by Similar Authors</option>
            <option value="gain">Recommend by Genres</option>
            <option value="maintain">Random Recommendation</option>
          </select>
        </label>
        <br />
        <button class="request_ex" type="submit">Recommend Books</button>
      </form>
    </section>
  );
}