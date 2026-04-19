import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { AnimatePresence } from "framer-motion";

import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import HistorySidebar from "./components/HistorySidebar";
import Footer from "./components/Footer";

function AnimatedRoutes({ isLoggedIn, setIsLoggedIn, setUsername }) {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route 
          path="/" 
          element={
            <Home 
              isLoggedIn={isLoggedIn} 
              username={setUsername ? localStorage.getItem("username") : ""} 
            />
          } 
        />
        <Route 
          path="/login" 
          element={
            <Login 
              setIsLoggedIn={setIsLoggedIn} 
              setUsername={setUsername}
            />
          } 
        />
      </Routes>
    </AnimatePresence>
  );
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [username, setUsername] = useState("");

  // Logout function
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    setIsLoggedIn(false);
    setUsername("");
  };

  // Check token on app load
  useEffect(() => {
    const token = localStorage.getItem("token");

    if (token) {
      try {
        const decoded = jwtDecode(token);

        if (decoded.exp * 1000 < Date.now()) {
          handleLogout();
        } else {
          setIsLoggedIn(true);
          setUsername(localStorage.getItem("username"));
        }
      } catch (err) {
        handleLogout();
      }
    }
  }, []);

  // Auto logout while app is running
  useEffect(() => {
    const interval = setInterval(() => {
      const token = localStorage.getItem("token");

      if (token) {
        try {
          const decoded = jwtDecode(token);

          if (decoded.exp * 1000 < Date.now()) {
            handleLogout();
          }
        } catch {
          handleLogout();
        }
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col">

        <Navbar
          isLoggedIn={isLoggedIn}
          setIsLoggedIn={setIsLoggedIn}
          openSidebar={() => setIsSidebarOpen(true)}
        />

        <div className="grow">
          <AnimatedRoutes
            isLoggedIn={isLoggedIn}
            setIsLoggedIn={setIsLoggedIn}
            setUsername={setUsername}
          />
        </div>

        <Footer />

        {/* Global Sidebar */}
        <HistorySidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />
      </div>
    </BrowserRouter>
  );
}

export default App;
