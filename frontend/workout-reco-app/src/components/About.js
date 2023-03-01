import React from 'react';
import TeamPage from './Team'
import './styles.css';
import './team.css'

export default function AboutUsSection() {
  const members = [
    { name: 'Francisco Heshiki', role: 'ML Engineer', link: 'https://www.linkedin.com/in/francisco-heshiki-de-las-casas-46a3491b5', image: require('/Users/fheshiki/Documents/GitHub/gymworkouts/frontend/workout-reco-app/src/images/paco.jpg') },
    { name: 'Alejandro Galvez', role: 'UX / UI Designer', link: 'https://www.linkedin.com/in/alejandro-g%C3%A1lvez-lopez-1ba9b8203/', image: require('/Users/fheshiki/Documents/GitHub/gymworkouts/frontend/workout-reco-app/src/images/ale.jpg')},
    { name: 'Ismael Doukkali', role: 'Project Manager', link: 'https://www.linkedin.com/in/ismael-doukkali/', image: require('/Users/fheshiki/Documents/GitHub/gymworkouts/frontend/workout-reco-app/src/images/isma.jpg')},
    { name: 'Vera Prohaska', role: 'ML Engineer', link: 'https://www.linkedin.com/in/vera-prohaska-31734b1b5/', image: require('/Users/fheshiki/Documents/GitHub/gymworkouts/frontend/workout-reco-app/src/images/vera.jpg')},
    { name: 'Zane Reda', role: 'Product Owner', link: 'https://www.linkedin.com/in/zane-reda-0992b3211/', image: require('/Users/fheshiki/Documents/GitHub/gymworkouts/frontend/workout-reco-app/src/images/zane.gif')}
  ];

  return (
    <div>
      <p className=''>About us</p>
      <div className='rowT'>
        <TeamPage member={members[0]} />
        <TeamPage member={members[1]} />
        <TeamPage member={members[2]} />
        <TeamPage member={members[3]} />
        <TeamPage member={members[4]} />
      </div>
    </div>
  );
}