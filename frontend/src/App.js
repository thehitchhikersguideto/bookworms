import React from 'react';
import TitleSection from './components/Title';
import DescriptionSection from './components/Description';
import BookSearch from './components/BookSearch';
import GithubSection from './components/Github';
import AboutUsSection from './components/About';
import ScrollToButton from "./components/ScrollButton";
import "./index.css"

export default function App() {

  const buttonConfigs = [
    { label: 'Start', targetId: 'section1', offset: 400 },
    { label: 'Description', targetId: 'section2', offset: 100 },
    { label: 'Recommender', targetId: 'section3', offset: 225 },    
    { label: 'GitHub', targetId: 'section4', offset: 275 },    
    { label: 'Meet the Team', targetId: 'section5', offset: 100 },  
  ];

  return (
    <div className="App">
      <ScrollToButton buttons={buttonConfigs} />
      <div id="section1">
        <TitleSection />
      </div>
      <div id="section2">
        <DescriptionSection />
      </div>
      <div id="section3">
        <BookSearch />
      </div>
      <div id="section4">
        <GithubSection />
      </div>
      <div id="section5">
        <AboutUsSection />
      </div>
    </div>
  );
}