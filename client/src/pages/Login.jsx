import { useState } from "react";

function Login({ setIsLoggedIn }) {

  const [isRegister, setIsRegister] = useState(false);

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

    if (isRegister && formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {

      const url = isRegister
        ? "http://localhost:8000/auth/register"
        : "http://localhost:8000/auth/login";

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

        setIsLoggedIn(true);

      } else {

        alert("Registration successful. Please login.");
        setIsRegister(false);

      }

    } catch (err) {
      setError(err.message);
    }
  };


  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fffbf5]">

      <div className="w-full bg-white rounded-lg shadow sm:max-w-md">

        <div className="p-6 space-y-5">

          <h2 className="text-2xl font-bold text-[#036666]">
            {isRegister ? "Register" : "Login"}
          </h2>

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
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
              className="w-full bg-[#358F80] text-white py-2 hover:bg-[#248277] rounded-full"
            >
              {isRegister ? "Register" : "Login"}
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

    </div>
  );
}

export default Login;