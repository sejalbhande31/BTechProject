let currentObject = "Stars";
let currentAnswer = 0;
let score = 0;
let timer;

const objects = [
  { name: "Stars", count: 8, image: "/static/images/star.png", options: [2, 3, 8, 5] },
  { name: "Balls", count: 6, image: "/static/images/ball.png", options: [1, 6, 4, 8] },
  { name: "Butterflies", count: 10, image: "/static/images/butterfly.png", options: [5, 7, 10, 8] },
  { name: "Flowers", count: 7, image: "/static/images/flower.png", options: [3, 5, 7, 8] },
  { name: "Rainbows", count: 4, image: "/static/images/rainbow.png", options: [3, 4, 6, 7] }
];

let currentRound = 0;

function loadGame() {
  const grid = document.getElementById("object-grid");
  const question = document.getElementById("question");
  const result = document.getElementById("result");
  const feedback = document.getElementById("feedback");
  const nextBtn = document.getElementById("next-btn");
  const scoreCount = document.getElementById("score-count");
  const optionsContainer = document.getElementById("options-container");
  
  const current = objects[currentRound];
  currentObject = current.name;
  currentAnswer = current.count;

  question.innerText = `How many ${currentObject}?`;
  grid.innerHTML = "";
  optionsContainer.innerHTML = "";

  for (let i = 0; i < current.count; i++) {
    const img = document.createElement("img");
    img.src = current.image;
    grid.appendChild(img);
  }

  shuffleArray(current.options).forEach(option => {
    const button = document.createElement("button");
    button.classList.add("option");
    button.innerText = option;
    button.onclick = () => checkAnswer(option, button);
    optionsContainer.appendChild(button);
  });

  result.innerText = "";
  feedback.innerText = "";
  nextBtn.style.display = "none";
  scoreCount.innerText = score;

  startTimer();
}

function checkAnswer(userAnswer, button) {
  const result = document.getElementById("result");
  const feedback = document.getElementById("feedback");

  // If the user has provided the correct answer
  if (userAnswer === currentAnswer) {
    result.innerText = "Correct!";
    result.style.color = "green";
    button.classList.add("correct");
    score++;
    disableButtons();
    clearInterval(timer);
    document.getElementById("next-btn").style.display = "block";

    // Clear the feedback message when the answer is correct
    feedback.innerText = ""; // Remove "Wrong answer" message
  } else {
    // If the answer is incorrect, show the "wrong answer" message
    feedback.innerText = "Wrong answer, try again!";
    feedback.style.color = "red";
  }

  updateScore();
}


function disableButtons() {
  const buttons = document.querySelectorAll('.options button');
  buttons.forEach(button => {
    button.classList.add("disabled");
    button.disabled = true;
  });
}

function nextRound() {
  currentRound++;
  if (currentRound >= objects.length) {
    showGameOver();
    return;
  }
  loadGame();
}

function startTimer() {
  const timerCount = document.getElementById("timer-count");
  let timeLeft = 15;
  timerCount.innerText = timeLeft;

  timer = setInterval(() => {
    timeLeft--;
    timerCount.innerText = timeLeft;

    if (timeLeft <= 0) {
      clearInterval(timer);
      document.getElementById("result").innerText = "Time's up!";
      disableButtons();
      document.getElementById("next-btn").style.display = "block";
    }
  }, 1000);
}

function updateScore() {
  document.getElementById("score-count").innerText = score;
}

function showGameOver() {
  document.getElementById("game-frame").classList.add("hidden");
  const scoreFrame = document.getElementById("score-frame");
  const finalScore = document.getElementById("final-score");
  finalScore.innerText = score;
  scoreFrame.classList.remove("hidden");
  
  const congratsAudio = document.getElementById("congrats-audio");
  congratsAudio.play();
}

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

loadGame();


function sendScoreToBackend(score, gameType) {
  fetch('/submit_score', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ score: score, game_type: gameType })
  })
    .then(response => response.json())
    .then(data => {
      console.log('Score saved:', data);
    })
    .catch(error => {
      console.error('Error saving score:', error);
    });
}

// Call this function at the end of the counting game
function showGameOver() {
  document.getElementById("game-frame").classList.add("hidden");
  const scoreFrame = document.getElementById("score-frame");
  const finalScore = document.getElementById("final-score");
  finalScore.innerText = score;
  scoreFrame.classList.remove("hidden");

  // Send score to backend
  sendScoreToBackend(score, "Counting Game");

  const congratsAudio = document.getElementById("congrats-audio");
  congratsAudio.play();
}


function submitScore(score) {
  fetch('/submit_score', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({
          score: score,
          game_type: 'Counting Game', // Specify your game type
      }),
  })
  .then(response => response.json())
  .then(data => {
      console.log(data.message || data.error);
  })
  .catch(error => console.error('Error:', error));
}

// Call this function when the game ends with the final score
// Example: submitScore(50);
