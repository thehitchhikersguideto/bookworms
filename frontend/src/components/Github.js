import React from 'react';
import './css/styles.css';
import './css/button.css'

export default function GithubSection() {
  return (
    <section className="git">
      <h2 className='subtitle'>Github</h2>
      <p className='git-text'>Check out our code!</p>
      <a href="https://github.com/thehitchhikersguideto/bookworms/" rel="noreferrer" target="_blank">
        <button className="button-33">Go to Github</button>
      </a>
    </section>
  );
}
