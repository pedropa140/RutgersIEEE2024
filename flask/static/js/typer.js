// Text for typing animation
const textToType = [
  "innovative engineers",
  "groundbreaking scientists",
  "inspiring leaders",
  "creative problem solvers",
];

// Function to simulate typing effect
let index = 0;
function typeText() {
  let currentText = "";
  let letterIndex = 0;

  const typingInterval = setInterval(() => {
    if (letterIndex < textToType[index].length) {
      currentText += textToType[index].charAt(letterIndex);
      // Add blinking cursor
      document.getElementById("typing-text").innerText = currentText + "|";
      letterIndex++;
    } else {
      clearInterval(typingInterval); // Stop the typing
      setTimeout(eraseText, 1500);
    }
  }, 100);

  function eraseText() {
    const eraseInterval = setInterval(() => {
      if (currentText.length > 0) {
        currentText = currentText.slice(0, -1);
        document.getElementById("typing-text").innerText = currentText + "|";
      } else {
        clearInterval(eraseInterval);
        document.getElementById("typing-text").innerText = ""; // Clear the text
        index = (index + 1) % textToType.length; // Move to the next string
        letterIndex = 0; // Reset letterIndex for the next word
        currentText = ""; // Reset currentText for the next word
        setTimeout(typeText, 500);
      }
    }, 50);
  }
}

// Initiate typing animation
window.onload = typeText;
