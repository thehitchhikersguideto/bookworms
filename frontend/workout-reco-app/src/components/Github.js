import React from 'react';
import './styles.css';


function GithubSection() {
  return (
    <section>
      <h2>Github</h2>
      <p>Check out our code on Github:</p>
      <a href="https://github.com/thehitchhikersguideto/gymworkouts" target="_blank" rel="noreferrer">
        <button class="gitButton">Go to Github</button>
      </a>
    </section>
  );
}

export default GithubSection;
