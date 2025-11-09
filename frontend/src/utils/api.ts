const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function newGame(type: string) {
  console.log(type);
  const r = await fetch(`${BASE}/games/new`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      difficulty: type,
    }),
  });
  if (!r.ok) throw new Error("newGame");
  return r.json();
}

export async function getBoardById(id: string) {
  const r = await fetch(`${BASE}/boards/${id}`);
  if (!r.ok) throw new Error("getBoardById");
  return r.json();
}

export async function validateBoard(state: string) {
  const r = await fetch(`${BASE}/games/validate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      board: { puzzle: state, state },
    }),
  });
  if (!r.ok) throw new Error("validate");
  return r.json();
}

export async function solveBoard(state: string) {
  const r = await fetch(`${BASE}/games/solve`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      board: { puzzle: state, state },
    }),
  });

  if (!r.ok) throw new Error("solve");
  return r.json();
}
