import React from 'react';
import './styles.css';


function AboutUsSection() {
  const members = [
    { name: 'Francisco Heshiki', role: 'ML Engineer' },
    { name: 'Alejandro Galvez', role: 'UX / UI Designer' },
    { name: 'Ismael Doukkali', role: 'Project Manager' },
    { name: 'Vera Prohaska', role: 'ML Engineer' },
    { name: 'Zane Reda', role: 'Product Owner' },
  ];
  

  return (
    <section class= "aboutus">
      <h2>About Us</h2>
      <ul>
        {members.map((member) => (
          <li key={member.name}>
            {member.name} - {member.role}
          </li>
        ))}
      </ul>
    </section>
  );
}

export default AboutUsSection;
