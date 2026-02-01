function TextInputComponent() {
  return (
    <div className="bg-white p-4 rounded-lg shadow mb-4">
      <h2 className="text-lg font-semibold mb-2">Text Input</h2>

      <textarea
        placeholder="Paste or type the text you want to fact-check..."
        className="w-full h-32 p-3 border border-gray-300 rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
      ></textarea>
    </div>
  );
}

export default TextInputComponent;
