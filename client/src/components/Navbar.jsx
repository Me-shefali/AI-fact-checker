import { useState } from "react";
import { Link } from "react-router-dom";
import HistorySidebar from "../components/HistorySidebar";

function Navbar({ isLoggedIn, setIsLoggedIn }) {

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <>
      <nav 
        className="sticky top-4 z-50 mx-6
          backdrop-blur-lg bg-white/70
          shadow-lg
          px-8 py-3
          flex justify-between items-center
          rounded-2xl
          border border-white/40"
      >

        {/* Left Side */}
        <div className="flex items-center space-x-3">
          <img 
            src="/validation.png" 
            className="h-8 w-8 object-contain" 
            alt="logo"
          />
          <h1 className="font-bold text-2xl text-[#036666]">
            AI Fact Checker
          </h1>
        </div>

        {/* Right Side */}
        <div className="flex items-center space-x-6 text-gray-700 font-medium">
          <Link
            to="/"
            className="relative px-3 py-1 transition duration-300 hover:text-[#036666]"
          >
            Home
          </Link>

          {isLoggedIn ? (
            <>
              <button
                onClick={() => setIsSidebarOpen(true)}
                className="hover:text-[#036666] transition"
              >
                History
              </button>
              <button
                onClick={() => {
                  localStorage.removeItem("token");
                  setIsLoggedIn(false);
                }}
                className="text-red-500 hover:text-red-700 transition"
              >
                Logout
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="hover:text-[#036666] transition"
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