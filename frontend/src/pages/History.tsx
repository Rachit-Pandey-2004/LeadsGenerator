import { FC } from "react";
import Navbar from "../components/Navbar";

interface HistoryItem {
  type: string;
  input: string;
  limit: number;
  date: string;
  status: "Completed" | "In Progress" | "Failed";
}

const dummyData: HistoryItem[] = [
  {
    type: "Hashtag",
    input: "#travel",
    limit: 100,
    date: "2025-04-10 10:30 AM",
    status: "Completed",
  },
  {
    type: "Followers",
    input: "elonmusk",
    limit: 50,
    date: "2025-04-09 6:12 PM",
    status: "In Progress",
  },
];

const History: FC = () => {
  const handleDownload = (item: HistoryItem) => {
    // TODO: Replace this with actual download logic or API call
    alert(`Downloading results for ${item.input}...`);
  };

  return (
    <div className="min-h-screen text-gray-800 overflow-x-hidden animate-gradient-slow"
    style={{
      backgroundImage:
        "linear-gradient(-45deg, #fef6e4, #e0f7fa, #fdf0ec, #e6f2f8)",
      backgroundSize: "200% 200%",
      animation: "gradientMove 15s ease infinite",
    }}>
      <Navbar />
      <main className="p-6">
        <h1 className="text-3xl font-bold mb-6 text-center">Scraping History</h1>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white shadow-md rounded-xl overflow-hidden">
            <thead className="bg-indigo-100">
              <tr>
                <th className="text-left py-3 px-4">Type</th>
                <th className="text-left py-3 px-4">Input</th>
                <th className="text-left py-3 px-4">Limit</th>
                <th className="text-left py-3 px-4">Date</th>
                <th className="text-left py-3 px-4">Status</th>
                <th className="text-left py-3 px-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {dummyData.map((item, idx) => (
                <tr key={idx} className="border-t">
                  <td className="py-3 px-4">{item.type}</td>
                  <td className="py-3 px-4">{item.input}</td>
                  <td className="py-3 px-4">{item.limit}</td>
                  <td className="py-3 px-4">{item.date}</td>
                  <td className="py-3 px-4">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        item.status === "Completed"
                          ? "bg-green-100 text-green-700"
                          : item.status === "In Progress"
                          ? "bg-yellow-100 text-yellow-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {item.status === "Completed" && (
                      <button
                        onClick={() => handleDownload(item)}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition"
                      >
                        Download
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {dummyData.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center py-6 text-gray-400">
                    No history found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
};

export default History;