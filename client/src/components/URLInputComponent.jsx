import { useState } from "react";

function URLInputComponent({ onResult }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  /* Validate URL format */
  const isValidUrl = (urlString) => {
    try {
      new URL(urlString);
      return true;
    } catch (e) {
      return false;
    }
  };

  /* Handle URL verification by sending to backend */
  const handleVerify = async () => {
    setError("");

    if (!url.trim()) {
      setError("Please enter a URL to verify");
      return;
    }

    if (!isValidUrl(url)) {
      setError("Please enter a valid URL (e.g., https://example.com)");
      return;
    }

    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/verify/url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      });
      const data = await response.json();
      onResult(data);
    } catch (error) {
      setError("Failed to verify URL. Please try again.");
      console.error("Error:", error);
    }
    setLoading(false);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      {/* URL input field */}
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter URL (e.g., https://example.com)..."
        className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* Error message display */}
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}

      {/* Verify button */}
      <button
        onClick={handleVerify}
        disabled={loading || !url.trim()}
        className="mt-3 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? "Verifying..." : "Verify URL"}
      </button>
    </div>
  );
}

export default URLInputComponent;
