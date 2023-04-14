import React from 'react';

export default function ResetButton({ onClick }) {
  return (
    <button className="reset_button" onClick={onClick}>
      Reset
    </button>
  );
}