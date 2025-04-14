import { FC } from "react";
import Navbar from "../components/Navbar";
import OptionSelector from "../components/OptionSelector";

const Home: FC = () => {
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
      <main className="p-24 flex flex-col items-center text-center space-y-6">
        <h1 className="text-3xl font-bold mb-4 opacity-0 animate-[fadeIn_0.8s_ease-out_forwards]">
          Welcome to Instagram Email Scraper . . .
        </h1>
        <div className="opacity-0 animate-[fadeIn_1s_ease-out_forwards]">
          <OptionSelector />
        </div>
      </main>
    </div>
  );
};

export default Home;