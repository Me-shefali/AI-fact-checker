import { Link } from "react-router-dom";

function Navbar({ isLoggedIn, setIsLoggedIn, openSidebar, username }) {
  return (
    <nav
      className="
        sticky top-4 z-50 mx-6
        backdrop-blur-lg bg-white/70
        shadow-lg
        px-8 py-3
        flex justify-between items-center
        rounded-2xl
        border border-white/40
      "
    >
      {/* LEFT */}
      <div className="flex items-center space-x-3">
        <img
          src="/validation.png"
          className="h-8 w-8 object-contain"
        />
        <h1 className="font-semibold text-xl text-[#036666]">
          AI Fact Checker
        </h1>
      </div>

      {/* RIGHT */}
      <div className="flex items-center space-x-6 text-gray-700 font-medium">

        <Link
          to="/"
          className="relative px-3 py-1 transition duration-300 hover:text-[#036666]"
        >
          Home
          <span className="absolute left-0 bottom-0 w-0 h-0.5 bg-[#036666] transition-all duration-300 hover:w-full"></span>
        </Link>

        {isLoggedIn ? (
          <>
            <span className="text-[#036666] font-semibold">
              {username}
            </span>

            <button
              onClick={openSidebar}
              className="hover:text-[#036666] transition"
            >
              History
            </button>

            <button
              onClick={() => setIsLoggedIn(false)}
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
  );
}

export default Navbar;