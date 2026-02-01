import { useState } from "react";
import { Link } from "react-router-dom";
import HistorySidebar from "../components/HistorySidebar";

function Navbar() {
  const isLoggedIn = false; // temporary
  
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <nav className="bg-white shadow px-6 py-4 flex justify-between">
      <h1 className="font-bold text-lg">AI Fact Checker</h1>

      <div className="space-x-4">
        <Link to="/">Home</Link>

        {!isLoggedIn ? (
          <Link to="/login">Login</Link>
        ) : (
          <button>Logout</button>
        )}

        <button
            onClick={() => setIsSidebarOpen(true)}
            >
            History
        </button>
        <HistorySidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        />
      </div>
    </nav>
  );
}

export default Navbar;
