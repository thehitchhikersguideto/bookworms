import React from 'react';

const RecommenderButton = ({ ratedBooks }) => {
    const apiurl = `${process.env.REACT_APP_API_URL}`;

    const handleRecommendation = async () => {
        console.log('Rated books:', ratedBooks);
        const response = await fetch(`${apiurl}/api/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(ratedBooks),
        });

        if (!response.ok) {
            throw new Error('Failed to retrieve recommendations');
        }

        console.log('Response:', response);

        const data = await response.json();
        console.log('Parsed response:', data);
        const books = data.map((book) => ({
            id: book.id,
            title: book.title,
            authors: book.authors.join(', '),
            image: book.image,
        }));
        console.log(books);
    };

  return (
    <button onClick={handleRecommendation}>
      Generate Recommendations
    </button>
  );
};

export default RecommenderButton;
