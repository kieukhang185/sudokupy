import React, { useEffect, useState } from "react";
import SudokuGrid from "./components/SudokuGrid";
import {
  parse,
  toCompact,
  loadLocal,
  saveLocal,
  formatTime,
  type Cell,
} from "./utils/board";
import { newGame, getBoardById, validateBoard, solveBoard } from "./utils/api";

type BoardType = "easy" | "medium" | "hard" | "master";
const STORAGE_KEY = "sudoku.single.player.v1";

export default function App() {
  const [cells, setCells] = useState<Cell[] | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [pencil, setPencil] = useState(false);
  const [boardType, setBoardType] = useState<BoardType>("medium");
  const [boardId, setBoardId] = useState<string | null>(null);
  const [boardIdInput, setBoardIdInput] = useState("");
  const [status, setStatus] = useState("");
  const [conflicts, setConflicts] = useState<Set<number>>(new Set());
  const [undoStack, setUndoStack] = useState<string[]>([]);
  const [redoStack, setRedoStack] = useState<string[]>([]);
  const [elapsed, setElapsed] = useState(0);
  const [startedAt, setStartedAt] = useState<number | null>(null);

  useEffect(() => {
    const saved = loadLocal(STORAGE_KEY);
    if (saved) {
      const d = JSON.parse(saved);
      const p = parse(d.state);
      setCells(p);
      setBoardType(d.boardType || "medium");
      setBoardId(d.boardId || null);
      setElapsed(d.elapsed || 0);
      setStartedAt(d.startedAt || Date.now());
      autoCheck(p);
    } else {
      startNew(boardType);
    }
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      if (startedAt) setElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(id);
  }, [startedAt]);

  useEffect(() => {
    if (!cells) return;
    saveLocal(
      STORAGE_KEY,
      JSON.stringify({
        state: toCompact(cells),
        boardType,
        boardId,
        elapsed,
        startedAt,
      }),
    );
  }, [cells, boardType, boardId, elapsed, startedAt]);

  async function startNew(type: BoardType) {
    const res = await newGame(type);
    const p = parse(res.puzzle);
    setCells(p);
    setBoardType(type);
    setBoardId(null);
    setUndoStack([]);
    setRedoStack([]);
    setConflicts(new Set());
    setStatus("");
    setStartedAt(Date.now());
    setElapsed(0);
    await autoCheck(p);
  }

  async function loadById(id: string) {
    const res = await getBoardById(id);
    const p = parse(res.initial_board);
    setCells(p);
    setBoardId(res.id);
    setBoardType(res.difficulty || "medium");
    setUndoStack([]);
    setRedoStack([]);
    setConflicts(new Set());
    setStatus("");
    setStartedAt(Date.now());
    setElapsed(0);
    await autoCheck(p);
  }

  async function autoCheck(c: Cell[] | null = null) {
    const cur = c ?? cells;
    if (!cur) return;
    const compact = toCompact(cur);
    try {
      const vr = await validateBoard(compact);
      setConflicts(new Set<number>(vr.conflicts || []));
      if (!vr.valid) {
        setStatus("Invalid");
        return;
      }
      if (vr.complete) {
        const sr = await solveBoard(compact);
        if (sr.solution === compact) {
          setStatus("🎉 Completed");
          alert(`🎉 Completed in ${formatTime(elapsed)}`);
        } else {
          setStatus("Filled but incorrect");
        }
      } else {
        setStatus("OK");
      }
    } catch {
      setStatus("Check failed");
    }
  }

  const onInput = async (d: number) => {
    if (!cells || selected == null) return;
    const cell = cells[selected];
    if (cell.given) return;
    const snap = toCompact(cells);
    setUndoStack((s) => [...s, snap]);
    setRedoStack([]);
    const next = cells.map((c, i) =>
      i !== selected
        ? c
        : pencil
          ? {
              ...c,
              notes: (() => {
                const n = new Set(c.notes);
                n.has(d) ? n.delete(d) : n.add(d);
                return n;
              })(),
            }
          : {
              ...c,
              value: d,
              notes: new Set<number>(),
            },
    );
    setCells(next);
    await autoCheck(next);
  };

  const onClear = async () => {
    if (!cells || selected == null) return;
    const cell = cells[selected];
    if (cell.given) return;
    const snap = toCompact(cells);
    setUndoStack((s) => [...s, snap]);
    setRedoStack([]);
    const next = cells.map((c, i) =>
      i === selected ? { ...c, value: 0, notes: new Set<number>() } : c,
    );
    setCells(next);
    await autoCheck(next);
  };
  const undo = async () => {
    if (!cells || undoStack.length === 0) return;
    const cur = toCompact(cells);
    const prev = undoStack[undoStack.length - 1];
    setUndoStack(undoStack.slice(0, -1));
    setRedoStack((r) => [...r, cur]);
    const p = parse(prev);
    setCells(p);
    await autoCheck(p);
  };
  const redo = async () => {
    if (!cells || redoStack.length === 0) return;
    const cur = toCompact(cells);
    const nxt = redoStack[redoStack.length - 1];
    setRedoStack(redoStack.slice(0, -1));
    setUndoStack((u) => [...u, cur]);
    const p = parse(nxt);
    setCells(p);
    await autoCheck(p);
  };

  if (!cells)
    return <div className="min-h-screen grid place-items-center">Loading…</div>;
  return (
    <div className="min-h-screen p-6 flex flex-col items-center gap-4">
      <h1 className="text-3xl font-bold">Sudoku — Single Player</h1>
      <div className="flex flex-wrap items-center gap-2">
        <label className="flex items-center gap-2">
          <span>Type</span>
          <select
            className="px-3 py-2 rounded-xl border"
            value={boardType}
            onChange={(e) => setBoardType(e.target.value as BoardType)}
          >
            <option value="easy">EASY</option>
            <option value="medium">MEDIUM</option>
            <option value="hard">HARD</option>
            <option value="master">MASTER</option>
          </select>
        </label>
        <button
          className="px-3 py-2 rounded-xl shadow bg-white hover:bg-gray-50"
          onClick={() => startNew(boardType)}
        >
          New Game
        </button>
        <div className="flex items-center gap-2">
          <input
            className="px-3 py-2 rounded-xl border"
            placeholder="Board ID"
            value={boardIdInput}
            onChange={(e) => setBoardIdInput(e.target.value)}
          />
          <button
            className="px-3 py-2 rounded-xl shadow bg-white hover:bg-gray-50"
            onClick={() => loadById(boardIdInput)}
          >
            Load by ID
          </button>
        </div>
        <span className="px-3 py-2 rounded-xl bg-gray-100">
          Status: {status || "—"}
        </span>
        <span className="px-3 py-2 rounded-xl bg-gray-100 font-mono">
          ⏱ {formatTime(elapsed)}
        </span>
      </div>
      <SudokuGrid
        cells={cells}
        selected={selected}
        pencil={pencil}
        conflicts={conflicts}
        onSelect={setSelected}
        onInput={onInput}
        onClear={onClear}
      />
      <div className="flex items-center gap-2">
        <button
          className="px-3 py-2 rounded-xl shadow bg-white hover:bg-gray-50"
          onClick={() => setPencil((p) => !p)}
        >
          {pencil ? "Pencil: ON" : "Pencil: OFF"}
        </button>
        <button
          className="px-3 py-2 rounded-xl shadow bg-white hover:bg-gray-50"
          onClick={undo}
          disabled={undoStack.length === 0}
        >
          Undo
        </button>
        <button
          className="px-3 py-2 rounded-xl shadow bg-white hover:bg-gray-50"
          onClick={redo}
          disabled={redoStack.length === 0}
        >
          Redo
        </button>
      </div>
      <KeyboardHandler onDigit={(n) => onInput(n)} onClear={() => onClear()} />
    </div>
  );
}
function KeyboardHandler({
  onDigit,
  onClear,
}: {
  onDigit: (n: number) => void;
  onClear: () => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key >= "1" && e.key <= "9") onDigit(Number(e.key));
      if (["Backspace", "Delete", "0"].includes(e.key)) onClear();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onDigit, onClear]);
  return null;
}
