import { useState } from "react";

function TextInputComponent({ onResult }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleVerify = async () => {
    setLoading(true);

    try {
      const token = localStorage.getItem("token");
       if (!token) {
        console.error("No auth token found. Is the user logged in?");
        setLoading(false);
        return;
      }
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
        setLoading(false);
        return;
      }
      const data = await response.json();
      onResult(data);

    } catch (error) {
      console.error("Error:", error);
    }

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
