import React from 'react';

const RecommenderButton = ({ ratedBooks, onRecommendations }) => {
    const apiurl = `${process.env.REACT_APP_API_URL}`;
    const cleanRatedBooks = ratedBooks.reduce((acc, book) => {
      acc.push({
        id: book.id,
        rating: book.rating
      });
      return acc;
    }, []);

    const parsedBooks = {"books": cleanRatedBooks};

    const handleRecommendation = async () => {
      try {
          const response = await fetch(`${apiurl}/api/recommend`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(parsedBooks),
          });
  
          if (!response.ok) {
              throw new Error('Failed to retrieve recommendations');
          }
  
          const data = await response.json();
          const books = data.map((book) => ({
              id: book.id,
              title: book.title,
              author: book.author,
              image: book.image,
          }));
  
          onRecommendations(books);
  
      } catch (err) {
          console.log(err);
      }
  };  

  return (
    <div style={{justifyContent: "center"}}>
      <button className='button-33' onClick={handleRecommendation}>
        Generate Recommendations
      </button>
    </div>
    
  );
};

export default RecommenderButton;
