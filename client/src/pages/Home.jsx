import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

import TextInputComponent from "../components/TextInputComponent";
import FileUploadComponent from "../components/FileUploadComponent";
import URLInputComponent from "../components/URLInputComponent";
import ResultComponent from "../components/ResultComponent";
import Card from "../components/Card";

function Home({ isLoggedIn, username }) {
  const [activeInput, setActiveInput] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleResult = (data) => {
    setResult(data);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="bg-white flex flex-col items-center px-6 py-10"
    >

      {/* HEADER */}
      <div className="w-full max-w-6xl text-center mb-4 mt-4">
        <AnimatePresence mode="wait">
          <motion.h2
            key={activeInput || "default"}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="text-3xl font-semibold text-[#036666]"
          >
            {activeInput === "text" && "Verify your text"}
            {activeInput === "url" && "Analyze a URL"}
            {activeInput === "file" && "Upload a document"}

            {!activeInput &&
              (isLoggedIn
                ? `Hey, ${username}! What's on your mind?`
                : "Let's, Fact Check!")}
          </motion.h2>
        </AnimatePresence>
      </div>

      {/* PARAGRAPH */}
      <AnimatePresence mode="wait">
        <motion.p
          key={activeInput || "default-text"}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="text-lg text-gray-600 max-w-2xl text-center mb-10"
        >
          {activeInput === "text" && "Paste your content below to verify its accuracy."}
          {activeInput === "url" && "Enter a URL to check claims from an article."}
          {activeInput === "file" && "Upload a document (PDF/DOCX) to analyze."}

          {!activeInput &&
            "Enter text, a URL, or upload a document to verify its accuracy."}
        </motion.p>
      </AnimatePresence>

      {/* MAIN CONTENT TRANSITION */}
      <AnimatePresence mode="wait">
        {!activeInput ? (
          <motion.div
            key="cards"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="w-full max-w-7xl"
          >
            <div className="grid gap-8 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 justify-items-center">
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
          </motion.div>
        ) : (
          <motion.div
            key="input"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="w-full max-w-4xl"
          >
            <button
              onClick={() => {
                setActiveInput(null);
                setResult(null);
              }}
              className="mb-4 px-4 py-2 bg-[#2d6a4f] text-white rounded hover:bg-[#2d6a4f]/80 shadow-md"
            >
              Change input type
            </button>

            {activeInput === "text" && (
              <TextInputComponent onResult={handleResult} setIsLoading={setIsLoading} />
            )}

            {activeInput === "url" && (
              <URLInputComponent onResult={handleResult} setIsLoading={setIsLoading} />
            )}

            {activeInput === "file" && (
              <FileUploadComponent onResult={handleResult} setIsLoading={setIsLoading} />
            )}

            {/* LOADING */}
            {isLoading && (
              <div className="mt-10 flex justify-center">
                <p className="text-lg text-gray-500 font-medium animate-pulse">
                  Processing your request...
                </p>
              </div>
            )}

            {/* RESULT */}
            <AnimatePresence>
              {!isLoading && result && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 15 }}
                  transition={{ duration: 0.4 }}
                  className="mt-6"
                >
                  <ResultComponent
                    result={result}
                    onBack={() => setResult(null)}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default Home;