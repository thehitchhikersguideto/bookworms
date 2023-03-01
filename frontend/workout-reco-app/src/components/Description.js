import React from 'react';
import './styles.css';

export default function DescriptionSection() {
  return (
    <section>
      <p className='minititle' style={{marginTop: 300}}>What is it?</p>
      <p class="description">The workout/exercise recommender is a tool that helps you create a customized workout routine based on your individual needs. Whether you're a beginner or an experienced fitness enthusiast, this tool can help you find exercises that are perfect for you.<br/>
      <br/>To get started, you'll answer a few questions about your fitness level, goals, and preferences. Based on your responses, the workout exercise recommender will generate a list of exercises that are tailored to your specific needs. These exercises might include cardio, strength training, flexibility, or a combination of all three.</p>
    </section>
  );
}