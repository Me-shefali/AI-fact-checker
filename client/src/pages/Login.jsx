import { useState } from "react";

function Login() {
  const [isRegister, setIsRegister] = useState(false);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-6 rounded-lg shadow w-full max-w-md">
        <h2 className="text-2xl font-bold mb-4 text-center">
          {isRegister ? "Register" : "Login"}
        </h2>

        <form className="space-y-4">
          {isRegister && (
            <input
              type="email"
              placeholder="Email"
              className="w-full p-2 border rounded"
            />
          )}

          <input
            type="text"
            placeholder="Username"
            className="w-full p-2 border rounded"
          />

          <input
            type="password"
            placeholder="Password"
            className="w-full p-2 border rounded"
          />

          {isRegister && (
            <input
              type="password"
              placeholder="Confirm Password"
              className="w-full p-2 border rounded"
            />
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          >
            {isRegister ? "Register" : "Login"}
          </button>
        </form>

        <p className="mt-4 text-sm text-center">
          {isRegister ? "Already have an account?" : "New user?"}{" "}
          <button
            onClick={() => setIsRegister(!isRegister)}
            className="text-blue-600 underline"
          >
            {isRegister ? "Login" : "Register"}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;
