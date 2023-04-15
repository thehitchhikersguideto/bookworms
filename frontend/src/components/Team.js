import React from 'react';
import './css/team.css'

const TeamPage = ({member}) => {
    const name = member.name.split(' ');

    return (
      <div className="columnT">
          <div className="cardT">
            <img className='image' src={member.image} alt={member.name} style={{ width:200 }}/>
            <div className="containerT">
              <h2>{name[0]} <br/> {name[1]}</h2>
              <p className="titleT">{member.role}</p>
              <a href={member.link} rel="noreferrer" target='_blank'><button className="buttonT">Contact</button></a>
            </div>
          </div>
        </div>
    );
  }

export default TeamPage;