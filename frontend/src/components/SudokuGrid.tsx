import React, { useMemo } from "react";
import type { Cell } from "../utils/board";

type Props = {
  cells: Cell[];
  selected: number | null;
  pencil: boolean;
  conflicts: Set<number>;
  onSelect: (i: number) => void;
  onInput: (n: number) => void;
  onClear: () => void;
};

const rowOf = (i: number) => Math.floor(i / 9);
const colOf = (i: number) => i % 9;

export default function SudokuGrid({
  cells,
  selected,
  pencil,
  conflicts,
  onSelect,
  onInput,
  onClear,
}: Props) {
  const selVal = selected != null ? cells[selected].value : 0;

  // Row/Col/Box + same-number highlights
  const hi = useMemo(() => {
    if (selected == null)
      return {
        row: new Set<number>(),
        col: new Set<number>(),
        box: new Set<number>(),
        same: new Set<number>(),
      };

    const r = rowOf(selected);
    const c = colOf(selected);
    const row = new Set<number>();
    const col = new Set<number>();
    const box = new Set<number>();
    const same = new Set<number>();

    for (let i = 0; i < 9; i++) {
      row.add(r * 9 + i);
      col.add(i * 9 + c);
    }
    const br = Math.floor(r / 3) * 3;
    const bc = Math.floor(c / 3) * 3;
    for (let dr = 0; dr < 3; dr++)
      for (let dc = 0; dc < 3; dc++) box.add((br + dr) * 9 + (bc + dc));

    if (selVal !== 0) {
      cells.forEach((cell, idx) => {
        if (cell.value === selVal) same.add(idx);
      });
    }
    return { row, col, box, same };
  }, [cells, selected, selVal]);

  // Digits completed across ALL 3×3 boxes → ✓ on number strip
  const completedDigits = useMemo(() => {
    const filledByBox = Array.from({ length: 9 }, () => new Set<number>());
    cells.forEach((cell, idx) => {
      if (cell.value > 0) {
        const r = rowOf(idx),
          c = colOf(idx);
        const b = Math.floor(r / 3) * 3 + Math.floor(c / 3);
        filledByBox[b].add(cell.value);
      }
    });
    const done = new Set<number>();
    for (let n = 1; n <= 9; n++)
      if (filledByBox.every((s) => s.has(n))) done.add(n);
    return done;
  }, [cells]);

  return (
    <div className="grid gap-3">
      {/* Number strip */}
      <div className="flex flex-wrap gap-2 justify-center">
        {Array.from({ length: 9 }, (_, i) => i + 1).map((n) => {
          const isDone = completedDigits.has(n);
          const active =
            selected != null && !pencil && cells[selected].value === n;
          return (
            <button
              key={n}
              onClick={() => onInput(n)}
              disabled={selected == null}
              className={[
                "w-10 h-10 rounded-xl text-lg font-semibold border border-gray-300 shadow-sm hover:bg-gray-50",
                selected == null ? "opacity-40 cursor-not-allowed" : "",
                isDone ? "bg-green-100 text-green-700" : "",
                active ? "ring-2 ring-blue-500" : "",
              ].join(" ")}
            >
              {isDone ? "✓" : n}
            </button>
          );
        })}
        <button
          onClick={onClear}
          disabled={selected == null}
          className="px-3 py-2 rounded-xl shadow bg-white hover:bg-gray-50 border border-gray-300 disabled:opacity-40"
        >
          Clear
        </button>
        <span className="px-3 py-2 rounded-xl bg-gray-100">
          {pencil ? "Pencil" : "Normal"}
        </span>
      </div>

      {/* Board wrapper */}
      <div className="relative w-full max-w-[560px] mx-auto overflow-hidden bg-white">
        {/* Lock aspect */}
        <div className="aspect-square" />

        {/* CELLS (z-10) */}
        <div className="absolute inset-0 grid grid-cols-9 grid-rows-9 select-none z-10">
          {cells.map((cell, idx) => {
            const isSel = selected === idx;
            const inRow = hi.row.has(idx);
            const inCol = hi.col.has(idx);
            const inBox = hi.box.has(idx);
            const isSame = hi.same.has(idx);
            const inConflict = conflicts.has(idx);

            const bg = isSel
              ? "bg-yellow-200"
              : inConflict
                ? "bg-red-50"
                : isSame
                  ? "bg-blue-100"
                  : inRow || inCol || inBox
                    ? "bg-gray-100"
                    : "bg-white";

            return (
              <button
                key={idx}
                type="button"
                onClick={() => onSelect(idx)}
                className={[
                  "relative w-full h-full focus:outline-none",
                  bg,
                  isSame && !isSel ? "ring-2 ring-blue-400 ring-inset" : "",
                  isSel ? "ring-2 ring-yellow-500 ring-inset" : "",
                ].join(" ")}
              >
                <div className="absolute inset-0 flex items-center justify-center">
                  {cell.value !== 0 ? (
                    <span className="leading-none font-semibold text-[min(5.2vw,28px)] md:text-2xl text-gray-900">
                      {cell.value}
                    </span>
                  ) : (
                    <div className="grid grid-cols-3 grid-rows-3 gap-[1px] w-4/5 h-4/5 opacity-80">
                      {Array.from({ length: 9 }, (_, i) => i + 1).map((n) => (
                        <div
                          key={n}
                          className="flex items-center justify-center text-[10px] md:text-xs text-gray-500"
                        >
                          {cell.notes.has(n) ? n : ""}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* THIN GRID OVERLAY (z-30): uniform 1px lines for all cell boundaries */}
        <div
          className="absolute inset-0 pointer-events-none z-30"
          style={{
            backgroundImage: `
              linear-gradient(to right, rgba(0,0,0,0.22) 1px, transparent 1px),
              linear-gradient(to bottom, rgba(0,0,0,0.22) 1px, transparent 1px)
            `,
            backgroundSize: `calc(100% / 9) 100%, 100% calc(100% / 9)`,
            backgroundPosition: `0 0, 0 0`,
          }}
        />

        {/* THICK 3×3 BORDERS (z-40): only special, darker lines */}
        {["0%", "33.3333%", "66.6667%", "100%"].map((left, i) => (
          <div
            key={`v-${i}`}
            className="absolute top-0 bottom-0 w-[2px] bg-gray-800 pointer-events-none z-40"
            style={{
              left,
              transform: left === "100%" ? "translateX(-1.5px)" : undefined,
            }}
          />
        ))}
        {["0%", "33.3333%", "66.6667%", "100%"].map((top, i) => (
          <div
            key={`h-${i}`}
            className="absolute left-0 right-0 h-[2px] bg-gray-800 pointer-events-none z-40"
            style={{
              top,
              transform: top === "100%" ? "translateY(-1.5px)" : undefined,
            }}
          />
        ))}
      </div>
    </div>
  );
}
