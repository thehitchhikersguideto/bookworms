import React from 'react';
import './styles.css';


export default function GithubSection() {
  return (
    <section class="git">
      <h2>Github</h2>
      <p className='git-text'>Check out our code on Github:</p>
      <a href="https://github.com/thehitchhikersguideto/gymworkouts" target="_blank" rel="noreferrer">
        <button class="gitButton">Go to Github</button>
      </a>
    </section>
  );
}
