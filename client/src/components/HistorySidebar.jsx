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
      .then(data => setHistory(data))
      .catch(err => console.log(err));

  }, [isOpen]);


  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40"
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-80 bg-white shadow-lg z-50 transform transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >

        {/* Header */}
        <div className="p-4 border-b flex justify-between items-center">
          <h3 className="font-semibold text-lg">History</h3>
          <button onClick={onClose}>✕</button>
        </div>

        {/* History List */}
        <div className="p-4 space-y-3 overflow-y-auto h-[90%]">

          {history.length === 0 && (
            <p className="text-sm text-gray-600">
              No history yet
            </p>
          )}

          {history.map(item => (
            <div
              key={item.id}
              className="border-b pb-2"
            >

              <p className="text-sm font-medium">
                {item.claim.slice(0,80)}...
              </p>

              <p className="text-xs text-gray-500">
                Verdict: {item.verdict}
              </p>

              <p className="text-xs text-gray-400">
                Similarity: {item.similarity.toFixed(2)}
              </p>

            </div>
          ))}

        </div>

      </div>
    </>
  );
}

export default HistorySidebar;