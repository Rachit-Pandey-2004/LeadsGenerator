import { FC, ReactNode } from "react";

type OptionCardProps = {
  title: string;
  description: string;
  icon: ReactNode;
  onClick: () => void;
};

const OptionCard: FC<OptionCardProps> = ({ title, description, icon, onClick }) => {
  return (
    <div
      className="hover:shadow-xl duration-300 ease-in-out transform hover:-translate-y-1 cursor-pointer bg-white hover:bg-gradient-to-tr from-cyan-50 via-neutral-50 to-teal-50 transition shadow-md rounded-2xl p-5 text-gray-800 flex flex-col items-center text-center space-y-2 border border-gray-200"
      onClick={onClick}
    >
      <div className="text-indigo-500 text-4xl">{icon}</div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
};

export default OptionCard;