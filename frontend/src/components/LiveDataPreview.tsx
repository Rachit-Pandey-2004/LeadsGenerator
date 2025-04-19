import { FC, useState, useEffect } from "react";
import { Download } from "lucide-react";

interface Props {
  searchId: string;
}

interface LiveUserData {
  username: string;
  email: string[];
  bio: string;
  account_type: number;
}

const LiveDataPreview: FC<Props> = ({ searchId }) => {
  const [emailFilter, setEmailFilter] = useState("all");
  const [accountTypeFilter, setAccountTypeFilter] = useState("all");
  const [liveData, setLiveData] = useState<LiveUserData[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res =  await fetch("http://0.0.0.0:8080/api/history",
          {
            method : 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: 'preview' ,id: searchId}),
          }
        );
        const json = await res.json();
        setLiveData(json.data || []);
      } catch (err) {
        console.error("Failed to fetch live data", err);
      }
    };

    fetchData();
  }, [searchId]);

  const filteredData = liveData.filter((user) => {
    const emailPass =
      emailFilter === "with_email"
        ? user.email.length > 0
        : emailFilter === "without_email"
        ? user.email.length === 0
        : true;

    const accountTypePass =
      accountTypeFilter === "all"
        ? true
        : user.account_type === parseInt(accountTypeFilter);

    return emailPass && accountTypePass;
  });

  const handleDownloadCSV = () => {
    window.open(`/api/download-csv/${searchId}`, "_blank");
  };

  const handleDownloadFilteredCSV = () => {
    const csvRows = [
      ["Username", "Email(s)", "Bio"],
      ...filteredData.map((user) => [
        user.username,
        user.email.join("; "),
        user.bio.replace(/\n/g, " "),
      ]),
    ];

    const csvContent =
      "data:text/csv;charset=utf-8," +
      csvRows.map((row) => row.map((col) => `"${col}"`).join(",")).join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `filtered_data_${searchId}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="p-4">
      <div className="flex flex-wrap items-center justify-between mb-4 gap-2">
        <h2 className="font-semibold text-gray-700 text-lg">Live Data</h2>
        <div className="flex gap-2 flex-wrap">
          <select
            value={emailFilter}
            onChange={(e) => setEmailFilter(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value="all">All Emails</option>
            <option value="with_email">With Email</option>
            <option value="without_email">Without Email</option>
          </select>

          <select
            value={accountTypeFilter}
            onChange={(e) => setAccountTypeFilter(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value="all">All Types</option>
            <option value="1">Personal</option>
            <option value="2">Business</option>
            <option value="3">Professional</option>
          </select>

          <button
            onClick={handleDownloadCSV}
            className="flex items-center gap-1 bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition"
          >
            <Download className="w-4 h-4" />
            Full CSV
          </button>

          <button
            onClick={handleDownloadFilteredCSV}
            className="flex items-center gap-1 bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 transition"
          >
            <Download className="w-4 h-4" />
            Filtered CSV
          </button>
        </div>
      </div>

      <table className="w-full text-sm border border-gray-200 rounded overflow-hidden">
        <thead className="bg-gray-100">
          <tr>
            <th className="text-left px-2 py-1">Username</th>
            <th className="text-left px-2 py-1">Email(s)</th>
            <th className="text-left px-2 py-1">Bio</th>
          </tr>
        </thead>
        <tbody>
          {filteredData.map((user, i) => (
            <tr key={i} className="border-t border-gray-200 even:bg-gray-50 hover:bg-gray-100">
              <td className="px-2 py-2 font-medium text-gray-800">{user.username}</td>
              <td className="px-2 py-2">
                {user.email.length > 0 ? (
                  <ul className="list-disc ml-4">
                    {user.email.map((em, j) => (
                      <li key={j}>{em}</li>
                    ))}
                  </ul>
                ) : (
                  <span className="text-gray-400 italic">N/A</span>
                )}
              </td>
              <td className="px-2 py-2 whitespace-pre-line">{user.bio}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LiveDataPreview;