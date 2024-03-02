import React from "react";
import PickStation from "../Assets/pick_station.png";
import ChoosePort from "../Assets/choose_port.png";
import SimulationResult from "../Assets/simulation_result.png";
import {
  subtitle
} from "./Text"

const Work = () => {
  const workInfoData = [
    {
      image: PickStation,
      title: "Select Charging Stations",
      text: "Select the charging stations to be used for the simulation",
    },
    {
      image: ChoosePort,
      title: "Charger Port",
      text: "Choose the type of charger (Level 1, 2, or 3 Supercharger) that will be used",
    },
    {
      image: SimulationResult,
      title: "Simulation Results",
      text: "Average wait time and cost will be calculated using an efficient and realistic stochastic model",
    }
  ];
  return (
    <div className="work-section-wrapper">
      <div className="work-section-top">
        <p className="primary-subheading">Work</p>
        <h1 className="primary-heading">How It Works</h1>
        <p className="primary-text">
          {subtitle}
        </p>
      </div>
      <div className="work-section-bottom">
        {workInfoData.map((data) => (
          <div className="work-section-info" key={data.title}>
            <div className="info-boxes-img-container">
              <img src={data.image} alt="" />
            </div>
            <h2>{data.title}</h2>
            <p>{data.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Work;