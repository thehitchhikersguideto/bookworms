import React from 'react';
import './css/ratingPopup.css';

function RatingPopup({ book, onRatingSelected }) {
  const handleRatingClick = (event, value) => {
    event.preventDefault();
    event.stopPropagation();
    onRatingSelected(book, value);
  };

  return (
    <>
      <div className="rating-popup">
        <h4 className='rating-text'>Rate this book:</h4>
        <div className="star-rating">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              className="star"
              onClick={(event) => handleRatingClick(event, star)}
            >
              &#9733;
            </button>
          ))}
        </div>
      </div>
    </>
  );
}

export default RatingPopup;