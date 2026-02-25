import React from "react";
// import PropTypes from "prop-types";

// outer div -> relative overflow-hidden w-60 h-80 rounded-3xl cursor-pointer text-2xl font-bold bg-purple-400
// 

function Card({ title, description, onClick}){
    return (
        <div
            onClick = {onClick}
            className="relative overflow-hidden w-full max-w-xs h-80 rounded-3xl flex items-center justify-center cursor-pointer text-2xl font-bold bg-[#67B99A]"
        >
            <div className="z-10 absolute w-full h-full peer"></div>
            <div
                className="absolute peer-hover:-top-20 peer-hover:-left-16 peer-hover:w-[140%] peer-hover:h-[140%] -top-32 -left-16 w-32 h-44 rounded-full bg-[#78C6A3] transition-all duration-500"
            ></div>
            <div
                className="absolute flex text-xl text-center items-end justify-end peer-hover:right-0 peer-hover:rounded-b-none peer-hover:bottom-0 peer-hover:items-center peer-hover:justify-center peer-hover:w-full peer-hover:h-full -bottom-32 -right-16 w-36 h-44 rounded-full bg-[#78C6A3] transition-all duration-500 text-white"
            >
                {description}
            </div>
            <div className="w-full h-full items-center justify-center flex uppercase text-white">
                {title}
            </div>
        </div>

    );
}

// Card.propTypes = {
//     title: PropTypes.string.isRequired,
//     description: PropTypes.string.isRequired,
//     onClick: PropTypes.func.isRequired,
// }

export default Card;