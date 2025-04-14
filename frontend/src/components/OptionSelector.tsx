import { FC, useState } from "react";
import { toast } from "sonner";
import OptionCard from "../components/OptionCards";
import {
  Tag,
  User,
  UserCheck,
  MessageCircle,
  MapPin,
  Heart,
} from "lucide-react";

const options = [
  {
    title: "Hashtags",
    description: "Search posts by hashtags (e.g., #nature, #tech)",
    icon: <Tag className="w-6 h-6" />,
  },
  {
    title: "Followers",
    description: "Scrape list of followers from a target user",
    icon: <User className="w-6 h-6" />,
  },
  {
    title: "Following",
    description: "Scrape the users a target user follows",
    icon: <UserCheck className="w-6 h-6" />,
  },
  {
    title: "Comments",
    description: "Find users/email from post comments",
    icon: <MessageCircle className="w-6 h-6" />,
  },
  {
    title: "Location",
    description: "Scrape based on tagged locations on posts",
    icon: <MapPin className="w-6 h-6" />,
  },
  {
    title: "Post Likes",
    description: "Find users who liked a specific post",
    icon: <Heart className="w-6 h-6" />,
  },
];

const OptionSelector: FC = () => {
  const [activeOption, setActiveOption] = useState<string | null>(null);
  const getPlaceholder = () => {
    switch (activeOption) {
      case "Hashtags":
        return "# Enter hashtags (use commas for multiple)";
      case "Followers":
        return "Enter target user's ID to get followers";
      case "Following":
        return "Enter target user's ID to get following";
      case "Comments":
        return "Enter post URL or ID to scan comments";
      case "Location":
        return "Enter location tag or place name";
      case "Post Likes":
        return "Enter post URL or ID to fetch likers";
      default:
        return "Enter input";
    }
  };
  return (
    <div className="p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {options.map((opt) => (
          <OptionCard
            key={opt.title}
            title={opt.title}
            description={opt.description}
            icon={opt.icon}
            onClick={() => setActiveOption(opt.title)}
          />
        ))}
      </div>

      {activeOption && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 w-full max-w-md shadow-xl text-gray-800">
            <h2 className="text-xl font-semibold mb-4">Configure: {activeOption}</h2>

            <form
              onSubmit={async (e) => {
                e.preventDefault();
                const input = (e.currentTarget.elements[0] as HTMLInputElement).value.replace(/\s+/g, '');
                const input_array = input.split(",")
                const limit = (e.currentTarget.elements[1] as HTMLInputElement).value;
                console.log("Submitted:", activeOption);
                // if (activeOption == "Hashtags"){
                //     const input= input.split(" ")
                // }
                console.log(input)
                console.log(limit)
                try {
                    const res = await fetch("http://0.0.0.0:8080/api/process", {
                      method: "POST",
                      headers: {
                        "Content-Type": "application/json",
                      },
                      
                      body: JSON.stringify({
                        "req_type": activeOption,
                        "query": input_array,
                        "limit" : Number(limit)
                      }),
                    });
              
                    const data = await res.json();
                    if(await res.status == 200){
                        toast.success(`Started processing ${activeOption}!`)
                    }
                    else{
                        toast.error(`Failed to process ${activeOption}`)
                    }
                    console.log("Response:", data);
                    
                    // TODO: handle success like toast or storing job status
                  } catch (err) {
                    console.error("Error during API call:", err);
                    toast.error(`Failed to process ${activeOption}`)
                    // TODO: show error to user
                  }
                setActiveOption(null);
              }}
              className="space-y-4"
            >
              <input
                type="text"
                placeholder={
                  getPlaceholder()
                }
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
              <input
                type="number"
                min="-1"
                placeholder="Limit (e.g., 1060) and -1 for no limit"
                className="w-full p-3 rounded-lg border border-gray-300 mb-6 focus:outline-none focus:ring-2 focus:ring-indigo-400"
              />
              <div className="flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setActiveOption(null)}
                  className="px-4 py-2 rounded-md bg-gray-200 hover:bg-gray-300 text-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-md bg-indigo-500 hover:bg-indigo-600 text-white"
                >
                  Confirm
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default OptionSelector;