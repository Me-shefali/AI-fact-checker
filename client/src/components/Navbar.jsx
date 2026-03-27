import { useState } from "react";
import { Link } from "react-router-dom";
import HistorySidebar from "../components/HistorySidebar";

// FIX: Navbar owns the sidebar state itself.
// The old code accepted openSidebar as a prop that was never passed from App,
// and rendered isSidebarOpen state that was never used to open the sidebar.
function Navbar({ isLoggedIn, setIsLoggedIn }) {

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <>
      <nav className="bg-[#fffbf5] shadow px-10 py-4 flex justify-between border-1 border-[#67B99A] transition-all duration-500 rounded-2xl">
        <div className="flex items-center space-x-3">
          <img src="/validation.png" className="h-9 w-9 object-contain" />
          <h1 className="font-bold text-2xl text-[#036666]">AI Fact Checker</h1>
        </div>

        <div className="flex items-center space-x-6 text-gray-700 font-medium">
          <Link
            to="/"
            className="transition duration-200 border-2 border-transparent rounded-full px-4 py-2 hover:border-[#036666]"
          >
            Home
          </Link>

          {isLoggedIn ? (
            <>
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="transition duration-200 border-2 border-transparent rounded-full px-4 py-2 hover:border-[#036666]"
              >
                History
              </button>
              <button
                onClick={() => {
                  localStorage.removeItem("token");   // FIX: also clears token on logout
                  setIsLoggedIn(false);
                }}
                className="text-red-600 hover:text-red-800 transition duration-200 border-2 border-transparent rounded-full px-4 py-2 hover:border-red-700"
              >
                Logout
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="transition duration-200 border-2 border-transparent rounded-full px-4 py-2 hover:border-[#036666]"
            >
              Login
            </Link>
          )}
        </div>
      </nav>

      {/* Sidebar rendered here so it sits outside nav flow */}
      <HistorySidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />
    </>
  );
}

export default Navbar;