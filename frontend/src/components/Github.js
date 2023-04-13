import React from 'react';
import './css/styles.css';


export default function GithubSection() {
  return (
    <section className="git">
      <h2>Github</h2>
      <p className='git-text'>Check out our code on Github:</p>
      <a href="https://github.com/thehitchhikersguideto/bookworms/" target="_blank" rel="noreferrer">
        <button className="gitButton">Go to Github</button>
      </a>
    </section>
  );
}
