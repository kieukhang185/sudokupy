import React from "react";
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

export default function SudokuGrid({
  cells,
  selected,
  pencil,
  conflicts,
  onSelect,
  onInput,
  onClear,
}: Props) {
  return (
    <div className="grid gap-3">
      <div className="grid grid-cols-9 gap-[2px] p-2 bg-gray-200 rounded-xl shadow">
        {cells.map((cell, idx) => {
          const isSel = selected === idx,
            inConflict = conflicts.has(idx);
          const borderClasses = [
            idx % 9 === 0 ? "border-l-2" : "",
            (idx + 1) % 9 === 0 ? "border-r-2" : "",
            Math.floor(idx / 9) % 3 === 0 ? "border-t-2" : "",
            Math.floor(idx / 9) % 3 === 2 ? "border-b-2" : "",
          ].join(" ");
          return (
            <button
              key={idx}
              onClick={() => onSelect(idx)}
              className={`aspect-square relative bg-white text-center flex items-center justify-center border border-gray-300 ${borderClasses} rounded-sm ${
                isSel ? "ring-2 ring-blue-400" : ""
              } ${cell.given ? "bg-gray-50 font-semibold" : ""} ${
                inConflict ? "bg-red-50 ring-2 ring-red-400" : ""
              }`}
            >
              {cell.value !== 0 ? (
                <span className="text-xl">{cell.value}</span>
              ) : (
                <div className="grid grid-cols-3 gap-0.5 w-full h-full p-0.5">
                  {Array.from({ length: 9 }, (_, i) => i + 1).map((n) => (
                    <span
                      key={n}
                      className="text-[10px] text-gray-400 leading-4 text-center"
                    >
                      {cell.notes.has(n) ? n : ""}
                    </span>
                  ))}
                </div>
              )}
            </button>
          );
        })}
      </div>
      <div className="flex items-center gap-2 flex-wrap">
        <div className="grid grid-cols-9 gap-2">
          {Array.from({ length: 9 }, (_, i) => i + 1).map((n) => (
            <button
              key={n}
              className="px-3 py-2 rounded-xl shadow bg-white hover:bg-gray-50"
              onClick={() => onInput(n)}
            >
              {n}
            </button>
          ))}
        </div>
        <button
          className="px-3 py-2 rounded-xl shadow bg-white hover:bg-gray-50"
          onClick={onClear}
        >
          Clear
        </button>
        <span className="px-3 py-2 rounded-xl bg-gray-100">
          {pencil ? "Pencil" : "Normal"}
        </span>
      </div>
    </div>
  );
}
