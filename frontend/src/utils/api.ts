let BASE = import.meta.env.VITE_API_BASE;

if (!BASE) {
  BASE =
    import.meta.env.MODE === "development" ? "http://localhost:8000" : "/api";
}

export const API_BASE = BASE;

export async function newGame(type: string) {
  const r = await fetch(`${API_BASE}/games/new`, {
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
  const r = await fetch(`${API_BASE}/boards/${id}`);
  if (!r.ok) throw new Error("getBoardById");
  return r.json();
}

export async function validateBoard(state: string) {
  const r = await fetch(`${API_BASE}/games/validate`, {
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
  const r = await fetch(`${API_BASE}/games/solve`, {
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
