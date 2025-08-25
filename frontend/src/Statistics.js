import React, { useEffect, useState } from "react";

export default function Statistics({ onBack }) {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchMetrics() {
      setLoading(true);
      try {
        const res = await fetch("/api/quiz/metrics");
        if (!res.ok) throw new Error("Failed to fetch metrics");
        const data = await res.json();
        setMetrics(data);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    fetchMetrics();
  }, []);

  let content;
  if (loading) {
    content = <div className="p-8">Loading statistics...</div>;
  } else if (error) {
    content = <div className="p-8 text-red-500">Error: {error}</div>;
  } else if (!metrics || !metrics.tally_by_command) {
    content = <div className="p-8">No data.</div>;
  } else {
    const commands = Object.keys(metrics.tally_by_command);
    const tallies = commands.map(cmd => metrics.tally_by_command[cmd]);
    const scores = commands.map(cmd => {
      const tally = metrics.tally_by_command[cmd];
      const total = tally.correct + tally.incorrect;
      return total > 0 ? tally.correct / total : 0;
    });

    content = (
      <div>
        <h2 className="text-2xl font-bold mb-4 text-gray-800">Command Score Heatmap</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full border">
            <thead>
              <tr>
                <th className="border px-2 py-1 bg-gray-200 text-gray-800">Command</th>
                <th className="border px-2 py-1 bg-gray-200 text-gray-800">Score</th>
              </tr>
            </thead>
            <tbody>
              {commands.map((cmd, i) => (
                <tr key={cmd}>
                  <td className="border px-2 py-1 font-mono text-gray-800">{cmd}</td>
                  <td
                    className="border px-2 py-1 relative text-gray-800"
                    style={{ background: `rgba(34,197,94,${scores[i]})` }}
                    title={`Correct: ${tallies[i].correct}, Incorrect: ${tallies[i].incorrect}`}
                  >
                    {(scores[i] * 100).toFixed(0)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 text-gray-600 text-sm">
          Total Guesses: {metrics.total_guesses}, Overall Score: {(metrics.score * 100).toFixed(2)}%
        </div>
      </div>
    );
  }

  return (
    <div
      className="fixed inset-0 bg-gray-800 bg-opacity-75 flex items-center justify-center"
      style={{ zIndex: 1000 }}
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onBack();
        }
      }}
    >
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-3xl w-full">
        <div style={{ position: "relative" }}>
          <a
            href="#"
            className="text-gray-800 text-xl font-bold hover:text-gray-600"
            style={{ position: "absolute", top: "5px", right: "5px", zIndex: 10 }}
            onClick={(e) => {
              e.preventDefault();
              onBack();
            }}
          >
            X
          </a>
          {content}
        </div>
      </div>
    </div>
  );
}
