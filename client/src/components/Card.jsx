import React from "react";

function Card({ title, description, icon, onClick }) {
  return (
    <div
      onClick={onClick}
      className="relative overflow-hidden w-full max-w-xs h-80 rounded-3xl 
                 flex flex-col items-center justify-center cursor-pointer 
                 bg-[#67B99A] text-white transition duration-300 hover:scale-105"
    >
      {/* Background animation */}
      <div className="absolute -top-20 -left-20 w-40 h-40 bg-[#78C6A3] rounded-full opacity-40"></div>
      <div className="absolute bottom-0 right-0 w-52 h-52 bg-[#78C6A3] rounded-full opacity-40"></div>

      {/* Content */}
      <div className="z-10 flex flex-col items-center text-center px-4">
        
        {/* ICON */}
        <img 
          src={icon} 
          alt={title} 
          className="w-16 h-16 mb-4 object-contain"
        />

        {/* TITLE */}
        <h3 className="text-xl font-bold uppercase mb-2">
          {title}
        </h3>

        {/* DESCRIPTION */}
        <p className="text-sm opacity-90">
          {description}
        </p>
      </div>
    </div>
  );
}

export default Card;