import React from "react";
// import BannerBackground from "../Assets/home-banner-background.png";
// import BannerImage from "../Assets/home-banner-image.png";
import Navbar from "../Components/Navbar";
import { FiArrowRight } from "react-icons/fi";

const Home = () => {
  return (
    <div className="home-container">
      <Navbar />
      <div className="home-banner-container">
        <div className="home-text-section">
          <h1 className="primary-heading">
            EV Charging Station Placement Simulator
          </h1>
          <p className="primary-text">
            This tool aims to support the MTO in identifying, evaluating, supporting, and prioritizing appropriate EV Charging station locations
          </p>
          <button className="secondary-button">
            View Map <FiArrowRight />{" "}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Home;