import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [mode, setMode] = useState<"single" | "vs-one" | "vs-two" | null>(null);
  const [level, setLevel] = useState("easy");
  const navigate = useNavigate();

  const startGame = () => {
    if (!mode) return;
    if (mode === "single") navigate(`/single/${level}`);
    if (mode === "vs-one") navigate(`/vs-one-board/${level}`);
    if (mode === "vs-two") navigate(`/vs-two-boards/${level}`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow p-6 md:p-8">
        <h1 className="text-3xl font-bold text-center mb-6">Sudoku</h1>
        <p className="text-center text-gray-600 mb-8">
          Choose a mode to start playing
        </p>

        <div className="grid gap-3 mb-6">
          <button
            onClick={() => setMode("single")}
            className={`px-4 py-3 rounded-xl font-semibold border shadow-sm ${
              mode === "single"
                ? "bg-blue-600 text-white"
                : "bg-white hover:bg-gray-50"
            }`}
          >
            Single Player
          </button>

          <button
            onClick={() => setMode("vs-one")}
            className={`px-4 py-3 rounded-xl font-semibold border shadow-sm ${
              mode === "vs-one"
                ? "bg-emerald-600 text-white"
                : "bg-white hover:bg-gray-50"
            }`}
          >
            2 vs 2 — One Board
          </button>

          <button
            onClick={() => setMode("vs-two")}
            className={`px-4 py-3 rounded-xl font-semibold border shadow-sm ${
              mode === "vs-two"
                ? "bg-purple-600 text-white"
                : "bg-white hover:bg-gray-50"
            }`}
          >
            2 vs 2 — Two Boards
          </button>
        </div>

        {mode && (
          <div className="border-t pt-6">
            <h2 className="text-center font-semibold mb-2">
              Select Difficulty
            </h2>
            <div className="flex justify-center gap-3 flex-wrap mb-6">
              {["easy", "medium", "hard", "expert", "master", "extreme"].map(
                (lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setLevel(lvl)}
                    className={`px-4 py-2 rounded-lg font-medium border shadow-sm ${
                      level === lvl
                        ? "bg-blue-500 text-white"
                        : "bg-white hover:bg-gray-50"
                    }`}
                  >
                    {lvl.toUpperCase()}
                  </button>
                ),
              )}
            </div>

            <div className="flex justify-center">
              <button
                onClick={startGame}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold"
              >
                Start Game
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
