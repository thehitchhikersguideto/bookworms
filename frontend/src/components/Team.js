import React from 'react';
import './css/team.css'

const TeamPage = ({member}) => {
    return (
      <div className="columnT">
          <div className="cardT">
            <img className='image' src={member.image} alt={member.name} style={{ width:200 }}/>
            <div className="containerT">
              <h2>{member.name}</h2>
              <p className="titleT">{member.role}</p>
              <p>{member.link}</p>
              <a href={member.link}><button className="buttonT" onClick={member.link}>Contact</button></a>
            </div>
          </div>
        </div>
    );
  }

export default TeamPage;