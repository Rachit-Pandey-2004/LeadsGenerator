import { FC } from "react";
import { Link, useLocation } from "react-router-dom";

const Navbar: FC = () => {
  const location = useLocation();

  const isActive = (path: string) =>
    location.pathname === path ? "text-blue-600 font-semibold" : "text-gray-600";

  return (
    <nav className="sticky top-4 z-50 mx-44 mt-4 bg-white rounded-xl shadow-sm px-6 py-3 flex items-center justify-between">
      <div className="text-xl font-winky font-bold text-cyan-800">
        Insta Scraper
      </div>
      <div className="space-x-6 text-sm">
        <Link to="/" className={isActive("/")}>
          Start
        </Link>
        <Link to="/history" className={isActive("/history")}>
          History
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;