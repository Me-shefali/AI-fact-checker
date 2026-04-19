import { useState } from "react";

function TextInputComponent({ onResult, setIsLoading }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleVerify = async () => {
    setError("");

    if (!text.trim()) {
      setError("Please enter some text to verify");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      setError("Please login to verify content");
      return;
    }

    setIsLoading(true);
    onResult(null);  //removes previous results
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        const err = await response.json();
        console.error("API error:", err.detail);
        setError(err.detail || "Verification failed");
        setLoading(false);
        return;
      }

      const data = await response.json();
      onResult(data);

    } catch (error) {
      setError("Network error. Please try again.");
      console.error("Error:", error);
    }

    setIsLoading(false);
    setLoading(false);
  };

  return (
    <div className="bg-white p-4 rounded-lg mb-4 flex-col items-center shadow-lg">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste text to fact-check..."
        className="w-full h-32 p-3 border border-grey-300 rounded"
      ></textarea>

      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      
      <button 
        onClick={handleVerify}
        disabled={loading}
        className="mt-2 px-4 py-2 bg-[#2d6a4f] text-white rounded hover:bg-[#2d6a4f]/80 shadow-md"
      >
        {loading ? "Verifying..." : "Verify"}
      </button>
    </div>
  );
}

export default TextInputComponent;
