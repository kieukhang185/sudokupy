import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

// pages
import Home from "./pages/Home";
import VersusOneBoard from "./pages/VersusOneBoard";
import VersusTwoBoards from "./pages/VersusTwoBoards";

// reuse your existing single-player page
import App from "./App"; // ← your current single-player file

import "./styles.css"; // tailwind or global css

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/single/:level" element={<App />} />
        <Route path="/vs-one-board/:level" element={<VersusOneBoard />} />
        <Route path="/vs-two-boards/:level" element={<VersusTwoBoards />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
