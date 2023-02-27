import React from 'react';
import { useEffect } from 'react';
import TitleSection from './components/TitleSection';
import DescriptionSection from './components/DescriptionSection';
import FormSection from './components/FormSection';
import GithubSection from './components/GithubSection';
import AboutUsSection from './components/AboutUsSection';

const [showSections, setShowSections] = useState(false);

useEffect(() => {
  const sections = document.querySelectorAll('.section');

  function checkSection() {
    sections.forEach(section => {
      const sectionTop = section.getBoundingClientRect().top;
      const windowHeight = window.innerHeight;
      if (sectionTop < windowHeight - 100) {
        section.classList.add('show');
      } else {
        section.classList.remove('show');
      }
    });
  }

  window.addEventListener('scroll', checkSection);

  setShowSections(true);

  return () => {
    window.removeEventListener('scroll', checkSection);
  }
}, []);


function App() {
  return (
    <div className="App">
      <TitleSection />
      <DescriptionSection />
      <FormSection />
      <GithubSection />
      <AboutUsSection />
    </div>
  );
}

export default App;
