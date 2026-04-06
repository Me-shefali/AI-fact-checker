import { useState } from "react";

function FileUploadComponent({ onResult }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ];

  /* Validate file before upload */
  const validateFile = (selectedFile) => {
    if (!selectedFile) {
      setError("Please select a file");
      return false;
    }

    if (!ALLOWED_TYPES.includes(selectedFile.type)) {
      setError("Only PDF and DOCX files are allowed");
      return false;
    }

    if (selectedFile.size > MAX_FILE_SIZE) {
      setError("File size must be less than 10MB");
      return false;
    }

    return true;
  };

  /* Handle file selection */
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setError("");
    
    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile);
    } else {
      setFile(null);
    }
  };

  /* Handle file upload and verification */
  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file to upload");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("token");

      if (!token) {
        setError("User not authenticated. Please login.");
        setLoading(false);
        return;
      }

      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/api/verify/file", {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + token
        },
        body: formData
      });

      if (!response.ok) {
        const err = await response.json();
        setError(err.detail || "File verification failed");
        setLoading(false);
        return;
      }

      const data = await response.json();
      onResult(data);
      setFile(null); // Clear file after successful upload
    } 
    catch (error) {
      setError("Failed to upload and verify file. Please try again.");
      console.error("Error:", error);
    }

    setLoading(false);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md mb-4">
      {/* File input */}
      <input
        type="file"
        onChange={handleFileChange}
        accept=".pdf,.docx"
        disabled={loading}
        className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* File info display */}
      {file && (
        <p className="text-sm text-gray-600 mt-2">
          Selected: {file.name} ({(file.size / 1024 / 1024).toFixed(2)}MB)
        </p>
      )}

      {/* Error message display */}
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}

      {/* Upload button */}
      <button
        onClick={handleUpload}
        disabled={loading || !file}
        className="mt-3 px-4 py-2 bg-[#2d6a4f] text-white rounded hover:bg-[#2d6a4f]/80 disabled:bg-gray-400"
      >
        {loading ? "Uploading..." : "Upload & Verify"}
      </button>
    </div>
  );
}

export default FileUploadComponent;
