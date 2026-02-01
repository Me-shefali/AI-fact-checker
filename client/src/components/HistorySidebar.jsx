function HistorySidebar({ isOpen, onClose }) {
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
        <div className="p-4 border-b flex justify-between items-center">
          <h3 className="font-semibold text-lg">History</h3>
          <button onClick={onClose}>✕</button>
        </div>

        <div className="p-4 text-sm text-gray-600">
          No history yet
        </div>
      </div>
    </>
  );
}

export default HistorySidebar;
