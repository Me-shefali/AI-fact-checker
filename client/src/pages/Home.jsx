import { useState } from "react";
import TextInputComponent from "../components/TextInputComponent";
import FileUploadComponent from "../components/FileUploadComponent";
import URLInputComponent from "../components/URLInputComponent";
import ResultComponent from "../components/ResultComponent";


function Home() {
  const [activeInput, setActiveInput] = useState(null);

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h2 className="text-2xl font-bold mb-6">Fact Check</h2>

      {/* Show selection cards ONLY when nothing is selected */}
      {!activeInput && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            onClick={() => setActiveInput("text")}
            className="cursor-pointer bg-white p-6 rounded-lg shadow hover:shadow-md"
          >
            <h3 className="text-lg font-semibold">Verify Text</h3>
            <p className="text-sm text-gray-600">
              Paste written content to verify facts
            </p>
          </div>

          <div
            onClick={() => setActiveInput("url")}
            className="cursor-pointer bg-white p-6 rounded-lg shadow hover:shadow-md"
          >
            <h3 className="text-lg font-semibold">Verify URL</h3>
            <p className="text-sm text-gray-600">
              Check claims from an online article
            </p>
          </div>

          <div
            onClick={() => setActiveInput("file")}
            className="cursor-pointer bg-white p-6 rounded-lg shadow hover:shadow-md"
          >
            <h3 className="text-lg font-semibold">Verify Document</h3>
            <p className="text-sm text-gray-600">
              Upload PDF or DOCX files
            </p>
          </div>
        </div>
      )}

      {/* Show input + result AFTER selection */}
      {activeInput && (
        <>
            <button
            onClick={() => setActiveInput(null)}
            className="mb-4 text-blue-600 underline"
            >
            ← Change input type
            </button>

            {activeInput === "text" && <TextInputComponent />}
            {activeInput === "url" && <URLInputComponent />}
            {activeInput === "file" && <FileUploadComponent />}

            <ResultComponent />
        </>
        )}
        
    </div>
  );
}

export default Home;
