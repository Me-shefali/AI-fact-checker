import { useState } from "react";
import TextInputComponent from "../components/TextInputComponent";
import FileUploadComponent from "../components/FileUploadComponent";
import URLInputComponent from "../components/URLInputComponent";
import ResultComponent from "../components/ResultComponent";
import Card from "../components/Card";

function Home({ isLoggedIn, username }) {
  const [activeInput, setActiveInput] = useState(null);
  const [result, setResult] = useState(null);

  return (
    <div className="min-h-screen bg-white flex flex-col items-center px-6 py-10">

      {/* HEADER */}
      <div className="w-full max-w-6xl text-center mb-4 mt-4">
        
        {isLoggedIn ? (
          <h2 className="text-3xl font-semibold text-[#036666]">
            Hey {username}, what do you want to know today?
          </h2>
        ) : (
          <h2 className="text-4xl font-bold text-[#036666]">
            Fact Check
          </h2>
        )}

      </div>

      {/* Paragraph */}
      <p className="text-lg text-gray-600 max-w-2xl text-center mb-10">
        Enter text, a URL, or upload a document to verify its accuracy.
      </p>

      {/* CARDS */}
      {!activeInput && (
        <div className="w-full max-w-6xl">
          <div className="grid gap-8 justify-items-center
                          grid-cols-1 
                          sm:grid-cols-2 
                          lg:grid-cols-3">

            <Card 
              title="Verify Text"
              description="Paste written content to verify facts"
              icon="/text.png"
              onClick={() => setActiveInput("text")}
            />

            <Card 
              title="Verify URL"
              description="Check claims from an online article"
              icon="/url.png"
              onClick={() => setActiveInput("url")}
            />

            <Card 
              title="Verify Document"
              description="Upload PDF or DOCX files"
              icon="/document.png"
              onClick={() => setActiveInput("file")}
            />

          </div>
        </div>
      )}

      {/* INPUT SECTION */}
      {activeInput && (
        <div className="w-full max-w-4xl">

          <button
            onClick={() => setActiveInput(null)}
            className="mb-4 px-4 py-2 bg-[#2d6a4f] text-white rounded hover:bg-[#2d6a4f]/80 shadow-md"
          >
            Change input type
          </button>

          {activeInput === "text" && <TextInputComponent onResult={setResult} />}
          {activeInput === "url" && <URLInputComponent onResult={setResult} />}
          {activeInput === "file" && <FileUploadComponent onResult={setResult} />}

          {result && (
            <ResultComponent 
              result={result} 
              onBack={() => setResult(null)} 
            />
          )}

        </div>
      )}
    </div>
  );
}

export default Home;