import { useEffect, useState } from "react";

function HistorySidebar({ isOpen, onClose }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!isOpen) return;

    fetch("http://localhost:8000/api/history", {
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token")
      }
    })
      .then(res => res.json())
      .then(data => {
        setHistory(Array.isArray(data) ? data : []);
      })
      .catch(err => console.log(err));
  }, [isOpen]);

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-100 transition-opacity"
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-[85%] sm:w-80 z-110 transform transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="h-full bg-white/80 backdrop-blur-lg shadow-2xl border-r border-gray-200 flex flex-col">

          {/* Header */}
          <div className="p-5 border-b flex justify-between items-center">
            <h3 className="text-xl font-semibold text-[#036666]">
              History
            </h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-red-500 transition text-lg"
            >
              ✕
            </button>
          </div>

          {/* Content */}
          <div className="p-4 space-y-4 overflow-y-auto flex-1">

            {history.length === 0 && (
              <p className="text-sm text-gray-500 text-center mt-10">
                No history yet
              </p>
            )}

            {history.map(item => (
              <div
                key={item.id}
                className="bg-white rounded-xl p-3 shadow-sm border hover:shadow-md transition"
              >
                <p className="text-sm font-medium text-gray-800 mb-1">
                  {item.claim.slice(0, 80)}...
                </p>

                <div className="text-xs space-y-1">
                  <p className="text-gray-600">
                    Verdict: <span className="font-semibold text-[#036666]">{item.verdict}</span>
                  </p>

                  <p className="text-gray-500">
                    Confidence:{" "}
                    {(item.confidence ?? item.similarity)?.toFixed(2)}
                  </p>
                </div>
              </div>
            ))}

          </div>
        </div>
      </div>
    </>
  );
}

export default HistorySidebar;