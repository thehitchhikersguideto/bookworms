import React from 'react';
import './css/styles.css';

export default function DescriptionSection() {
  return (
    <section>
      <p className='minititle' style={{marginTop: 300}}>What is it?</p>
      <p className="description">This book recommendation system is an algorithm that recommends books to readers based on various data points such as the user's reading history, book ratings, and preferences. The system uses machine learning algorithms to analyze the user's behavior, including the books they've read, rated, and reviewed, and generate personalized book recommendations.
      <br></br>The recommendation system might also consider other factors such as popular trends and ratings by other readers. The goal of the book recommendation system is to enhance the user's reading experience by helping them discover new books that they might enjoy, and encouraging them to continue reading.</p>
    </section>
  );
}