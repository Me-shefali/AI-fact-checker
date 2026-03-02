/*import React from 'react'

function ResultComponent() {
  return (
    <h1>Result</h1>
  )
}

export default ResultComponent*/
function ResultComponent({ result, onBack }) {
  if (!result) return null;

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      {/* Result header */}
      <h3 className="text-lg font-semibold mb-4">Verification Results</h3>

      {/* Display verification status */}
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          <strong>Status:</strong> 
          <span className={result.verified ? "text-green-600 ml-2" : "text-red-600 ml-2"}>
            {result.verified ? "Verified" : "Not Verified"}
          </span>
        </p>
      </div>

      {/* Display claims if available */}
      {result.claims && result.claims.length > 0 && (
        <div className="mb-4">
          <h4 className="font-semibold text-sm mb-2">Claims Found:</h4>
          <ul className="list-disc pl-5">
            {result.claims.map((claim, index) => (
              <li key={index} className="text-sm text-gray-700 mb-1">
                {claim}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Display confidence score if available */}
      {result.confidence !== undefined && (
        <div className="mb-4">
          <p className="text-sm text-gray-600">
            <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%
          </p>
        </div>
      )}

      {/* Back button */}
      <button
        onClick={onBack}
        className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
      >
        Back
      </button>
    </div>
  );
}

export default ResultComponent;