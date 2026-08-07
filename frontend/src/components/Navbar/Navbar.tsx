import { useScroll } from "@/context/ScrollContext";
import { useTranslation } from "react-i18next";

import LanguageSwitcher from "@/components/LanguageSwitcher/LanguageSwitcher";


import "./Navbar.scss";


function Navbar() {


  const {
    activeSection
  } = useScroll();


  const {
    t
  } = useTranslation();



  const scrollTo = (
    id: string
  ) => {

    document
      .getElementById(id)
      ?.scrollIntoView({
        behavior: "smooth"
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
          {t("nav.home")}
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
          {t("nav.recommendations")}
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
          {t("nav.shop")}
        </a>



      </div>




      <LanguageSwitcher />


    </nav>

  );

}


export default Navbar;