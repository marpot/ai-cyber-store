import { NavLink } from "react-router-dom";
import { useScroll } from "@/context/ScrollContext";

import "./Navbar.scss";


function Navbar() {


  const {
    activeSection
  } = useScroll();



  const scrollTo = (
    id:string
  ) => {


    document
      .getElementById(id)
      ?.scrollIntoView({
        behavior:"smooth"
      });


  };



  return (

    <nav className="navbar">


      <div className="navbar__logo">
        AI Cyber Store
      </div>



      <div className="navbar__links">


        <a
          className={
            activeSection === "home"
              ? "active"
              : ""
          }

          onClick={() =>
            scrollTo("home")
          }
        >
          Home
        </a>



        <a
          className={
            activeSection === "recommendations"
              ? "active"
              : ""
          }

          onClick={() =>
            scrollTo(
              "recommendations"
            )
          }
        >
          AI
        </a>



        <a
          className={
            activeSection === "shop"
              ? "active"
              : ""
          }

          onClick={() =>
            scrollTo("shop")
          }
        >
          Shop
        </a>


      </div>


    </nav>

  );
}


export default Navbar;