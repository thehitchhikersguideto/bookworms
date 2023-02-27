import React from 'react';
import ReactDOM from 'react-dom';
import TitleSection from './components/Title';
import DescriptionSection from './components/Description';
import FormSection from './components/Form';
import GithubSection from './components/Github';
import AboutUsSection from './components/About';
import './index.css';

function App() {
  return (
    <div className="container">
      <TitleSection />
      <DescriptionSection />
      <FormSection />
      <GithubSection />
      <AboutUsSection />
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));
