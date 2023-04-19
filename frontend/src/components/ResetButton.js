import React from "react";
import "./css/button.css"

function ResetButton() {
  const handleClick = () => {
    window.location.reload();
  };

  return (
    <button className="button-33" onClick={handleClick}>
      Reset
    </button>
  );
}

export default ResetButton;