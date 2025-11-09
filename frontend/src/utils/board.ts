export type Compact = string;

export type Cell = { value: number; notes: Set<number>; given: boolean };

export function parse(puzzle: Compact): Cell[] {
  return Array.from(puzzle).map((ch) => {
    const v = Number(ch);
    return {
      value: v,
      notes: new Set<number>(),
      given: v !== 0,
    };
  });
}

export function toCompact(cells: Pick<Cell, "value">[]): Compact {
  return cells.map((c) => String(c.value)).join("");
}

export function loadLocal(k: string): string | null {
  try {
    return localStorage.getItem(k);
  } catch {
    return null;
  }
}

export function saveLocal(k: string, v: string) {
  try {
    localStorage.setItem(k, v);
  } catch {}
}

export function formatTime(sec: number) {
  const h = String(Math.floor(sec / 3600)).padStart(2, "0");
  const m = String(Math.floor((sec % 3600) / 60)).padStart(2, "0");
  const s = String(Math.floor(sec % 60)).padStart(2, "0");
  return `${h}:${m}:${s}`;
}
