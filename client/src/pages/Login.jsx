import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

function Login({ setIsLoggedIn, setUsername }) {
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: ""
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (isRegister && formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    try {
      const BASE_URL = "http://localhost:8000";

      const url = isRegister
        ? `${BASE_URL}/auth/register`
        : `${BASE_URL}/auth/login`;

      const body = isRegister
        ? {
            email: formData.email,
            username: formData.username,
            password: formData.password
          }
        : {
            username: formData.username,
            password: formData.password
          };

      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Something went wrong");
      }

      if (!isRegister) {
        localStorage.setItem("token", data.access_token);
        // store username
        localStorage.setItem("username", data.username || formData.username);
        
        setIsLoggedIn(true);
        setUsername(data.username || formData.username);

        navigate("/");
      }

      else {
        alert("Registration successful. Please login.");
        setIsRegister(false);
      }

    } 
    catch (err) {
      setError(err.message || "Network error");
    }
    finally {
      setLoading(false);
    }
  };


  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -30 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="min-h-screen flex items-center justify-center bg-white"
    >

      <div className="w-full bg-white rounded-lg shadow sm:max-w-md">

        <div className="p-6 space-y-5">

          <h2 className="text-2xl font-bold text-[#036666]">
            {isRegister ? "Register" : "Login"}
          </h2>

          {error && (
            <p className={`text-sm ${
              error.includes("successful") ? "text-green-600" : "text-red-500"
            }`}>
              {error}
            </p>
          )}

          <form
            className="space-y-4"
            onSubmit={handleSubmit}
          >

            {isRegister && (
              <div>
                <label className="block mb-1 text-sm font-medium">
                  Email
                </label>

                <input
                  type="email"
                  name="email"
                  placeholder="Email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full p-2 border rounded-xl"
                  required
                />
              </div>
            )}

            <div>
              <label className="block mb-1 text-sm font-medium">
                Username
              </label>

              <input
                type="text"
                name="username"
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
                className="w-full p-2 border rounded-xl"
                required
              />
            </div>

            <div>
              <label className="block mb-1 text-sm font-medium">
                Password
              </label>

              <input
                type="password"
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
                className="w-full p-2 border rounded-xl"
                required
              />
            </div>

            {isRegister && (
              <div>
                <label className="block mb-1 text-sm font-medium">
                  Confirm Password
                </label>

                <input
                  type="password"
                  name="confirmPassword"
                  placeholder="Confirm Password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="w-full p-2 border rounded-xl"
                  required
                />
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#358F80] text-white py-2 hover:bg-[#248277] rounded-full"
            >
              {loading
                ? "Please wait..."
                : isRegister
                ? "Register"
                : "Login"}
            </button>

          </form>

          <p className="text-sm text-gray-500">

            {isRegister
              ? "Already have an account?"
              : "Don’t have an account yet?"}

            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError("");
              }}
              className="ml-2 text-[#358F80] hover:underline"
            >
              {isRegister ? "Login" : "Register"}
            </button>

          </p>

        </div>

      </div>

    </motion.div>
  );
}

export default Login;