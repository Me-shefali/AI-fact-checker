import { useState } from "react";

function Login({ setIsLoggedIn }) {
  const [isRegister, setIsRegister] = useState(false);

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#fffbf5]">
      <div className="w-full bg-white rounded-lg shadow md:mt-0 sm:max-w-md xl:p-0 ">
        <div className="p-6 space-y-4 md:space-y-6 sm:p-8">
          <h2 className="text-2xl font-bold leading-tight tracking-tight text-[#036666] md:text-2xl">
            {isRegister ? "Register" : "Login"}
          </h2>

          <form 
            className="space-y-4 md:space-y-6"
            onSubmit={(e) => {
            e.preventDefault();
            setIsLoggedIn(true);
          }}>
            {isRegister && (
              <div>
                <label 
                  for="email" 
                  className="block mb-2 text-sm font-medium text-gray-900">
                  Your email
                </label>
                <input
                  type="email"
                  name="email"
                  placeholder="Email"
                  className="w-full p-2 border rounded-xl"
                />
              </div>
            )}

            <div>
              <label 
                for="username" 
                className="block mb-2 text-sm font-medium text-gray-900">
                Username
              </label>
              <input
                type="text"
                name="username"
                placeholder="Username"
                className="w-full p-2 border rounded-xl"
              />
            </div>

            <div>
              <label 
                for="password" 
                className="block mb-2 text-sm font-medium text-gray-900">
                Password
              </label>
              <input
                type="password"
                name="password"
                placeholder="Password"
                className="w-full p-2 border rounded-xl"
              />
            </div>

            {isRegister && (
              <div>
                <label 
                for="confirmPassword" 
                className="block mb-2 text-sm font-medium text-gray-900 ">
                Confirm Password
              </label>
                  <input
                    type="password"
                    name="confirmPassword"
                    placeholder="Confirm Password"
                    className="w-full p-2 border rounded-xl"
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

          <p className="text-sm font-light text-gray-500 ">
            {isRegister ? "Already have an account?" : "Don’t have an account yet?"}{" "}
            <button
              onClick={() => setIsRegister(!isRegister)}
              className="font-medium text-[#358F80] hover:underline"
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
