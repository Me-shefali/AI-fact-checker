import { useState } from "react";
import TextInputComponent from "../components/TextInputComponent";
import FileUploadComponent from "../components/FileUploadComponent";
import URLInputComponent from "../components/URLInputComponent";
import ResultComponent from "../components/ResultComponent";
import Card from "../components/Card";

// ECE2D0  D7EBBA
function Home({ isLoggedIn }) {
  const [activeInput, setActiveInput] = useState(null);

  return (
    <div className="min-h-screen bg-[#fffbf5] flex flex-col items-center px-6 py-10">
      <div className="w-full max-w-6xl justify-items-center">
        <h2 className="text-4xl font-bold mb-6 text-[#036666] p-4">Fact Check</h2>
      </div>

        {/* Show selection cards ONLY when nothing is selected */}
        {!activeInput && (
          <div className="w-full max-w-6xl">
            <div className="grid gap-8 justify-items-center
                          grid-cols-1 
                          sm:grid-cols-2 
                          lg:grid-cols-3"
            >
              <Card 
                title="Verify Text"
                description="Paste written content to verify facts"
                onClick={() => setActiveInput("text")}
              />
              <Card 
                title="Verify URL"
                description="Check claims from an online article"
                onClick={() => setActiveInput("url")}
              />
              <Card 
                title="Verify Document"
                description="Upload PDF or DOCX files"
                onClick={() => setActiveInput("file")}
              />
            </div>
          </div>
        )}

        {/* Show input + result AFTER selection */}
        {activeInput && (
          <div className="w-full max-w-4xl">
              <button
              onClick={() => setActiveInput(null)}
              className="mb-4 underline"
              >
              ← Change input type
              </button>

              {activeInput === "text" && <TextInputComponent />}
              {activeInput === "url" && <URLInputComponent />}
              {activeInput === "file" && <FileUploadComponent />}

              <ResultComponent />
          </div>
          )}

    </div>
  );
}

export default Home;
