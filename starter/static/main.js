// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      const boxRow = Math.floor(i / 3);
      const boxCol = Math.floor(j / 3);
      const boxClass = (boxRow + boxCol) % 2 === 0
        ? 'box-shade'
        : 'box-plain';
      input.className = `sudoku-cell ${boxClass}`;
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateInvalidMoveState(e.target);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function getCurrentBoard() {
  const inputs = document.querySelectorAll('#sudoku-board input');
  const board = Array.from({length: SIZE}, () => Array(SIZE).fill(0));
  inputs.forEach((input) => {
    board[Number(input.dataset.row)][Number(input.dataset.col)] = input.value
      ? parseInt(input.value, 10)
      : 0;
  });
  return board;
}

function isInvalidMove(row, col, value, board) {
  for (let index = 0; index < SIZE; index++) {
    if (index !== col && board[row][index] === value) return true;
    if (index !== row && board[index][col] === value) return true;
  }
  const startRow = row - row % 3;
  const startCol = col - col % 3;
  for (let boxRow = startRow; boxRow < startRow + 3; boxRow++) {
    for (let boxCol = startCol; boxCol < startCol + 3; boxCol++) {
      if ((boxRow !== row || boxCol !== col) && board[boxRow][boxCol] === value) {
        return true;
      }
    }
  }
  return false;
}

function updateInvalidMoveState(input) {
  const feedbackEnabled = document.getElementById('instant-feedback').checked;
  input.classList.remove('invalid-move');
  if (!feedbackEnabled || !input.value) return;

  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const board = getCurrentBoard();
  if (isInvalidMove(row, col, board[row][col], board)) {
    input.classList.add('invalid-move');
  }
}

function updateAllInvalidMoveStates() {
  document.querySelectorAll('#sudoku-board input:not(:disabled)').forEach(updateInvalidMoveState);
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('incorrect', 'invalid-move');
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }
  if (incorrect.size === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = 'Puzzle solved correctly! Congratulations!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('instant-feedback').addEventListener('change', (e) => {
    if (!e.target.checked) {
      document.querySelectorAll('#sudoku-board input').forEach((input) => {
        input.classList.remove('invalid-move');
      });
      return;
    }
    updateAllInvalidMoveStates();
  });
  // initialize
  newGame();
});