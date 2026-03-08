function ResultComponent({ result, onBack }) {
  if (!result) return null;

  const results = result.results || [];

  // Determine overall status
  const isVerified = results.some(r => r.verdict === "True");

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-4">

      {/* Header */}
      <h3 className="text-xl font-semibold mb-4 text-gray-800">
        Verification Results
      </h3>

      {/* Overall Status */}
      <div className="mb-6">
        <p className="text-sm text-gray-600">
          <strong>Status:</strong>
          <span
            className={`ml-2 font-medium ${
              isVerified ? "text-green-600" : "text-red-600"
            }`}
          >
            {isVerified ? "Verified" : "Not Verified"}
          </span>
        </p>
      </div>

      {/* Results */}
      {results.length > 0 ? (
        <div className="space-y-4">
          {results.map((item, index) => (
            <div
              key={index}
              className="border rounded-lg p-4 bg-gray-50"
            >
              {/* Claim */}
              <p className="text-gray-800 mb-2">
                <strong>Claim:</strong> {item.claim}
              </p>

              {/* Verdict */}
              <p className="text-sm mb-1">
                <strong>Verdict:</strong>{" "}
                <span
                  className={
                    item.verdict === "True"
                      ? "text-green-600 font-medium"
                      : item.verdict === "False"
                      ? "text-red-600 font-medium"
                      : "text-yellow-600 font-medium"
                  }
                >
                  {item.verdict}
                </span>
              </p>

              {/* Similarity */}
              <p className="text-sm text-gray-600">
                <strong>Similarity:</strong>{" "}
                {(item.similarity * 100).toFixed(2)}%
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-sm">No claims detected.</p>
      )}

      {/* Back Button */}
      <button
        onClick={onBack}
        className="mt-6 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
      >
        Back
      </button>
    </div>
  );
}

export default ResultComponent;