import { FC, useEffect, useState } from "react";
import { RefreshCcw } from "lucide-react";
import Navbar from "../components/Navbar";
import LiveDataPreview from "../components/LiveDataPreview"; 
import { motion } from "framer-motion";
import { toast } from "sonner";

interface BackendHistoryItem {
  _id: string;
  status: "pending" | "failed" | "in_progress" | "completed";
  query_type: string;
  query: string[];
  limit: number;
  created_at: string;
}

const History: FC = () => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [history, setHistory] = useState<BackendHistoryItem[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchHistory = async () => {
    setIsRefreshing(true);
    setLoading(true);
    try {
      const res = await fetch("http://0.0.0.0:8080/api/history",
        {
          method : 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: 'listing' }),
        }
      );
      if( await res.status == 200 ) {
        toast.success("success!!")
      }
      else{
        toast.error(`failed with status code ${await res.status}`)
      } 
      const json = await res.json();
      setHistory(json.data);
    } catch (error) {
      console.error("Failed to fetch history:", error);
      toast.error("failed . . . ")
    }
    setLoading(false);
    setIsRefreshing(false);
  };

  const handleRestart = async (item: BackendHistoryItem) => {
    try {
      const res = await fetch("http://0.0.0.0:8080/api/history", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: "reset", id: item._id }),
      });
      if( await res.status == 200 ) {
        toast.success("success!!")
      }
      else{
        toast.error(`failed with status code ${await res.status}`)
      } 
      const result = await res.json();
      if (res.ok) {
        alert("Task reset successfully!");
        fetchHistory(); // Refresh the UI
      } else {
        alert("Failed to reset task: " + result.error);
      }
    } catch (error) {
      console.error("Reset error:", error);
      toast.error("Something went wrong while resetting.");
    }
  };
  useEffect(() => {
    fetchHistory();
  }, []);

  const getStatusBadge = (status: string) => {
    const styles = {
      completed: "bg-green-100 text-green-700",
      in_progress: "bg-yellow-100 text-yellow-700",
      failed: "bg-red-100 text-red-700",
      pending: "bg-gray-200 text-gray-600",
    };
    return (
      <span
        className={`px-3 py-1 rounded-full text-sm font-medium ${
          styles[status as keyof typeof styles]
        }`}
      >
        {status.replace("_", " ").replace(/\b\w/g, (l) => l.toUpperCase())}
      </span>
    );
  };

  return (
    <div
      className="min-h-screen text-gray-800 overflow-x-hidden animate-gradient-slow"
      style={{
        backgroundImage:
          "linear-gradient(-45deg, #fef6e4, #e0f7fa, #fdf0ec, #e6f2f8)",
        backgroundSize: "200% 200%",
        animation: "gradientMove 15s ease infinite",
      }}
    >
      <Navbar />
      <main className="p-6 animate-[fadeIn_0.8s_ease-out_forwards]">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-center w-full">Scraping History</h1>
          <button
            onClick={fetchHistory}
            className="ml-auto bg-white p-2 rounded-full shadow hover:bg-gray-100 transition"
            title="Refresh History"
          >
            <motion.div
              animate={{ rotate: isRefreshing ? 360 : 0 }}
              transition={{ repeat: isRefreshing ? Infinity : 0, duration: 1, ease: "linear" }}
            >
              <RefreshCcw className="w-5 h-5 text-gray-600" />
            </motion.div>
          </button>
        </div>
        <div className="overflow-x-auto ">
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
              {history.map((item) => (
                <>
                  <tr key={item._id} className="border-t">
                    <td className="py-3 px-4">{item.query_type}</td>
                    <td className="py-3 px-4">{item.query.join(", ")}</td>
                    <td className="py-3 px-4">{item.limit}</td>
                    <td className="py-3 px-4">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">{getStatusBadge(item.status)}</td>
                    <td className="py-3 px-4 space-x-2">
                      {item.status === "completed" && (
                        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition">
                          Download
                        </button>
                      )}
                      
                      <button
                        onClick={() =>
                          setExpandedId(expandedId === item._id ? null : item._id)
                        }
                        className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg text-sm hover:bg-gray-400 transition"
                      >
                        {expandedId === item._id ? "Hide" : "View"}
                      </button>
                      {item.status === "failed" && (
                        <button
                          onClick={() => handleRestart(item)}
                          className="px-4 py-2 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 transition"
                        >
                          Restart
                        </button>
                      )}
                    </td>
                  </tr>

                  {expandedId === item._id && (
                    <tr className="bg-gray-50">
                      <td colSpan={6}>
                        <LiveDataPreview searchId={item._id} />
                      </td>
                    </tr>
                  )}
                </>
              ))}
              {!loading && history.length === 0 && (
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