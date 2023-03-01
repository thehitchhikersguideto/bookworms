import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import './ScrollToButtons.css';

const ScrollToButtons = ({ buttons }) => {
  const [scrollPosition, setScrollPosition] = useState(0);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  const handleScroll = () => {
    setScrollPosition(window.pageYOffset);
  };

  const handleButtonClick = (targetId, offset) => {
    const targetElement = document.getElementById(targetId);

    if (targetElement) {
      const offsetPosition = targetElement.offsetTop - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      });
    }
  };

  return (
    <div className="scroll-to-buttons" style={{ position: 'fixed', top: 0 }}>
      {buttons.map(({ label, targetId, offset }, index) => (
        <button key={index} onClick={() => handleButtonClick(targetId, offset)}>
          {label}
        </button>
      ))}
    </div>
  );
};

ScrollToButtons.propTypes = {
  buttons: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      targetId: PropTypes.string.isRequired,
      offset: PropTypes.number.isRequired,
    })
  ).isRequired,
};

export default ScrollToButtons;
