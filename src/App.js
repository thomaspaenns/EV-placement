import './App.css';
import {
  BrowserRouter,
  createBrowserRouter,
  Routes,
  Route,
  RouterProvider,
} from "react-router-dom";
import Home from "./routes/Home";
import Map from "./routes/Map";
import Work from './Components/Works';
// import Testimonial from "./Components/Testimonial";
// import Contact from "./Components/Contact";
// import Footer from "./Components/Footer";

const router = createBrowserRouter([
  {
    path: "/",
    element: <div>Hello world!</div>,
  },
]);

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route index element={<Home />} />
          <Route path="/map" element={<Map />} />
        </Routes>
      </BrowserRouter>
      {/* <About />
      <Work />
      <Testimonial />
      <Contact />
      <Footer /> */}

    </div>
  );
}

export default App;