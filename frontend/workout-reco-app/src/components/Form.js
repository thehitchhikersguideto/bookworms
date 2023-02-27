import React, { useState } from 'react';
import './styles.css';


function FormSection() {
  const [age, setAge] = useState('');
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [goal, setGoal] = useState('');

  function handleSubmit(event) {
    event.preventDefault();
    // TODO: implement logic to recommend exercises based on input
  }

  return (
    <section>
      <h2>Recommend Exercises</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Age:
          <input type="number" value={age} onChange={(event) => setAge(event.target.value)} />
        </label>
        <br />
        <label>
          Weight (in kg):
          <input type="number" value={weight} onChange={(event) => setWeight(event.target.value)} />
        </label>
        <br />
        <label>
          Height (in cm):
          <input type="number" value={height} onChange={(event) => setHeight(event.target.value)} />
        </label>
        <br />
        <label>
          Goal:
          <select value={goal} onChange={(event) => setGoal(event.target.value)}>
            <option value="">--Select--</option>
            <option value="lose">Lose Weight</option>
            <option value="gain">Gain Muscle</option>
            <option value="maintain">Maintain Weight</option>
          </select>
        </label>
        <br />
        <button type="submit">Recommend Exercises</button>
      </form>
    </section>
  );
}

export default FormSection;
