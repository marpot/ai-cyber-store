import { useLocation, useNavigate } from "react-router-dom";
import { useScroll } from "@/context/ScrollContext";
import { useTranslation } from "react-i18next";

import LanguageSwitcher from "@/components/LanguageSwitcher/LanguageSwitcher";

import "./Navbar.scss";

function Navbar() {
  const {
    activeSection,
    scrollTo: contextScrollTo,
  } = useScroll();

  const {
    t,
  } = useTranslation();

  const location = useLocation();
  const navigate = useNavigate();

  const isProductPage =
    location.pathname.startsWith("/product/");

  const handleNavigation = (section: string) => {
    // Jesteśmy na stronie produktu
    if (isProductPage) {
      navigate("/");

      // Czekamy aż Home zostanie wyrenderowany
      setTimeout(() => {
        contextScrollTo(section);
      }, 100);

      return;
    }

    // Jesteśmy już na stronie głównej
    contextScrollTo(section);
  };

  return (
    <nav className="navbar">

      <div className="navbar__logo">
        AI Cyber Store
      </div>

      <div className="navbar__links">

        <a
          className={
            !isProductPage &&
            activeSection === "home"
              ? "active"
              : ""
          }
          onClick={() =>
            handleNavigation("home")
          }
        >
          {t("nav.home")}
        </a>

        <a
          className={
            !isProductPage &&
            activeSection === "recommendations"
              ? "active"
              : ""
          }
          onClick={() =>
            handleNavigation(
              "recommendations"
            )
          }
        >
          {t("nav.recommendations")}
        </a>

        <a
          className={
            isProductPage ||
            activeSection === "shop"
              ? "active"
              : ""
          }
          onClick={() =>
            handleNavigation("shop")
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