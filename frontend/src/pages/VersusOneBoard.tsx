import { Link } from "react-router-dom";

export default function VersusOneBoard() {
  return (
    <div className="min-h-screen p-6 flex flex-col items-center gap-4">
      <div className="w-full max-w-2xl bg-white rounded-2xl shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">2 vs 2 — One Board</h1>
          <Link to="/" className="text-blue-600 hover:underline">
            ← Home
          </Link>
        </div>
        <p className="text-gray-600">
          Placeholder screen. We’ll wire the shared board logic here later.
        </p>
      </div>
    </div>
  );
}
