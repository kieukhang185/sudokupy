import React, { useEffect, useMemo, useRef, useState } from "react";

// --- Sudoku logic ---
const SIZE = 9;
const BOX = 3;
const DIGITS = [1,2,3,4,5,6,7,8,9];

const emptyBoard = () => Array.from({ length: SIZE }, () => Array(SIZE).fill(0));
const clone = (board) => board.map(row => row.slice());
const row_Ok = (board, row, value) => !board[row].includes(v);
const col_Ok = (board, col, value) => !board.some(row => row[col] === value);
const box_Ok = (board, row, col, value) => {
  const row_0 = Math.floor(row / BOX) * BOX;
  const col_0 = Math.floor(col / BOX) * BOX;
  for (let rr = row_0; rr < row_0 + BOX; rr++) {
    for (let cc = col_0; cc < col_0 + BOX; cc++) {
      if (board[rr][cc] === value) return false;
    }
  }
  return true;
};
const valid = (board, row, col, value) => row_Ok(board, row, value) && col_Ok(board, col, value) && box_Ok(board, row, col, value);

const findEmpty = (board) => {
  for (let row = 0; row < SIZE; row++) for (let col = 0; col < SIZE; col++) if (board[row][col] === 0) return [row, col];
  return null;
};
const solve = (board) => {
  const spot = findEmpty(board);
  if (!spot) return true;
  const [row, col] = spot;
  for (const value of DIGITS) {
    if (valid(board, row, col, value)) {
      board[row][col] = value;
      if (solve(board)) return true;
      board[row][col] = 0;
    }
  }
  return false;
};
const randSample = (arr, k) => {
  const copy = arr.slice();
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, k);
};
const generateFullSolution = () => {
  const board = emptyBoard();
  for (let board_r = 0; board_r < SIZE; board_r += BOX) {
    const nums = randSample(DIGITS, BOX);
    for (let i = 0; i < BOX; i++) board[board_r + i][board_r + i] = nums[i];
  }
  solve(board);
  return board;
};
const makePuzzle = (holes = 45) => {
  const full = generateFullSolution();
  const puzzle = clone(full);
  const coords = [];
  for (let row = 0; row < SIZE; row++) for (let col = 0; col < SIZE; col++) coords.push([row, col]);
  for (let i = coords.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [coords[i], coords[j]] = [coords[j], coords[i]];
  }
  for (let i = 0; i < Math.min(holes, coords.length); i++) {
    const [row, col] = coords[i];
    puzzle[row][col] = 0;
  }
  return { puzzle, solution: full };
};
const boardsEqual = (a, b) => a.every((r, i) => r.every((v, j) => v === b[i][j]));

export default function SudokuWeb() {
  const [game, setGame] = useState(() => {
    const { puzzle, solution } = makePuzzle(47);
    return { puzzle, solution, working: clone(puzzle) };
  });
  const fixed = useMemo(() => game.puzzle.map(row => row.map(v => v !== 0)), [game.puzzle]);
  const [sel, setSel] = useState([0, 0]);
  const [msg, setMsg] = useState("");
  const [won, setWon] = useState(false);

  useEffect(() => {
    const onKey = (e) => {
      const [r, c] = sel;
      if (e.key === "ArrowRight" || e.key === "d") setSel([r, (c + 1) % SIZE]);
      else if (e.key === "ArrowLeft" || e.key === "a") setSel([r, (c + SIZE - 1) % SIZE]);
      else if (e.key === "ArrowDown" || e.key === "s") setSel([(r + 1) % SIZE, c]);
      else if (e.key === "ArrowUp" || e.key === "w") setSel([(r + SIZE - 1) % SIZE, c]);
      else if (["Backspace", "Delete", "0"].includes(e.key)) {
        if (!fixed[r][c] && !won) {
          const next = clone(game.working);
          next[r][c] = 0;
          setGame({ ...game, working: next });
          setMsg("");
        }
      } else if (/^[1-9]$/.test(e.key)) {
        if (!fixed[r][c] && !won) {
          const v = parseInt(e.key, 10);
          if (valid(game.working, r, c, v)) {
            const next = clone(game.working);
            next[r][c] = v;
            const isWin = boardsEqual(next, game.solution);
            setGame({ ...game, working: next });
            setWon(isWin);
            setMsg("");
          } else {
            setMsg(`'${v}' conflicts with row/col/box`);
          }
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sel, game, fixed, won]);

  const cellConflicts = useMemo(() => {
    const bad = new Set();
    const w = game.working;
    for (let r = 0; r < SIZE; r++) for (let c = 0; c < SIZE; c++) {
      const v = w[r][c];
      if (!v) continue;
      w[r][c] = 0;
      if (!valid(w, r, c, v)) bad.add(`${r},${c}`);
      w[r][c] = v;
    }
    return bad;
  }, [game.working]);

  const setValue = (r, c, v) => {
    if (fixed[r][c] || won) return;
    const next = clone(game.working);
    next[r][c] = v;
    if (v === 0 || valid(game.working, r, c, v)) {
      const isWin = v !== 0 && boardsEqual(next, game.solution);
      setGame({ ...game, working: next });
      setWon(isWin);
      setMsg("");
    } else {
      setMsg(`'${v}' conflicts with row/col/box`);
    }
  };

  const newPuzzle = (holes = 47) => {
    const { puzzle, solution } = makePuzzle(holes);
    setGame({ puzzle, solution, working: clone(puzzle) });
    setSel([0, 0]);
    setWon(false);
    setMsg("New puzzle.");
  };
  const clearBoard = () => { setGame({ ...game, working: clone(game.puzzle) }); setWon(false); setMsg("Cleared."); };
  const solveAll = () => { setGame({ ...game, working: clone(game.solution) }); setWon(true); setMsg("Solved."); };
  const hint = () => { 
    const [r, c] = sel;
    if (fixed[r][c] || won) return;
    const v = game.solution[r][c];
    if (v) setValue(r, c, v);
    setMsg("Hint used."); 
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-[720px]">
        <h1 className="text-2xl font-semibold mb-4">Sudoku (Web)</h1>

        <div className="grid grid-cols-9 bg-gray-300 p-[1px] rounded-lg select-none">
          {Array.from({ length: SIZE }).map((_, r) => (
            Array.from({ length: SIZE }).map((_, c) => {
              const v = game.working[r][c];
              const isFixed = fixed[r][c];
              const selected = sel[0] === r && sel[1] === c;
              const conflict = cellConflicts.has(`${r},${c}`);
              const thickBorder = `border border-gray-700 ${r % 3 === 0 ? 'border-t-[2px]' : ''} ${c % 3 === 0 ? 'border-l-[2px]' : ''} ${r === SIZE - 1 ? 'border-b-[2px]' : ''} ${c === SIZE - 1 ? 'border-r-[2px]' : ''}`;

              return (
                <button
                  key={`${r}-${c}`}
                  onClick={() => setSel([r, c])}
                  className={`h-14 sm:h-16 flex items-center justify-center text-lg ${thickBorder} ${selected ? 'bg-blue-100' : 'bg-white'} ${isFixed ? 'font-semibold text-blue-700' : 'text-gray-800'} ${conflict ? 'bg-red-100' : ''}`}
                >
                  {v === 0 ? '' : v}
                </button>
              );
            })
          ))}
        </div>

        <div className="mt-4 grid grid-cols-10 gap-2">
          {[1,2,3,4,5,6,7,8,9].map(n => (
            <button
              key={n}
              onClick={() => setValue(sel[0], sel[1], n)}
              className="py-2 rounded-md bg-gray-900 text-white hover:bg-gray-800"
            >{n}</button>
          ))}
          <button onClick={() => setValue(sel[0], sel[1], 0)} className="py-2 rounded-md bg-gray-200 hover:bg-gray-300">Erase</button>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          <button onClick={() => newPuzzle(47)} className="px-3 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-500">New</button>
          <button onClick={clearBoard} className="px-3 py-2 rounded-md bg-gray-200 hover:bg-gray-300">Clear</button>
          <button onClick={solveAll} className="px-3 py-2 rounded-md bg-green-600 text-white hover:bg-green-500">Solve</button>
          <button onClick={hint} className="px-3 py-2 rounded-md bg-yellow-400 text-black hover:bg-yellow-300">Hint</button>
        </div>

        <p className="mt-3 text-sm text-gray-700 h-6">{won ? '🎉 You solved it!' : msg}</p>
        <p className="mt-4 text-xs text-gray-500">Tips: click a cell and use your keyboard (1–9, arrows, Backspace/Delete). The UI highlights conflicting entries in red.</p>
      </div>
    </div>
  );
}