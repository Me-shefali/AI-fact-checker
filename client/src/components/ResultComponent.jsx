function ResultComponent({ result, onBack }) {
  if (!result) return null;

  const results = result.results || [];

  // 🔹 Improved overall status logic
  const hasTrue = results.some(r => r.verdict?.toLowerCase().includes("true"));
  const hasFalse = results.some(r => r.verdict?.toLowerCase().includes("false"));

  let overallStatus = "Unverified";
  let statusColor = "text-yellow-600";

  if (hasTrue && hasFalse) {
    overallStatus = "Mixed";
    statusColor = "text-yellow-600";
  } else if (hasFalse) {
    overallStatus = "Not Verified";
    statusColor = "text-red-600";
  } else if (hasTrue) {
    overallStatus = "Verified";
    statusColor = "text-green-600";
  }

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
          <span className={`ml-2 font-medium ${statusColor}`}>
            {overallStatus}
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
                    item.verdict?.toLowerCase().includes("true")
                      ? "text-green-600 font-medium"
                      : item.verdict?.toLowerCase().includes("false")
                      ? "text-red-600 font-medium"
                      : "text-yellow-600 font-medium"
                  }
                >
                  {item.verdict}
                </span>
              </p>

              {/* Confidence (replaces similarity) */}
              <p className="text-sm text-gray-600">
                <strong>Confidence:</strong>{" "}
                {item.confidence !== undefined
                  ? `${(item.confidence * 100).toFixed(2)}%`
                  : "N/A"}
              </p>

              {/* Evidence */}
              {item.evidence && item.evidence.length > 0 && (
                <div className="mt-2 space-y-1">
                  <p className="text-xs font-medium text-gray-500">
                    Evidence:
                  </p>

                  {item.evidence.map((ev, i) => (
                    <div key={i} className="text-xs text-gray-500">
                      <span className="font-medium text-gray-600">
                        {ev.source || ev.domain || 'Source'}:
                      </span>{" "}
                      {ev.text?.slice(0, 120)}...

                      {ev.url && (
                        <a
                          href={ev.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-500 underline ml-1"
                        >
                          source
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}

            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-sm">
          No claims detected.
        </p>
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