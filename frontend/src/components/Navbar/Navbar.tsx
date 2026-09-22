import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useScroll } from "@/context/ScrollContext";
import { useTranslation } from "react-i18next";

import LanguageSwitcher from "@/components/LanguageSwitcher/LanguageSwitcher";
import { useCart } from "@/context/CartContext";

import "./Navbar.scss";

function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  const {
    activeSection,
    scrollTo: contextScrollTo,
  } = useScroll();

  const { t } = useTranslation();

  const location = useLocation();
  const navigate = useNavigate();

  const { cart } = useCart();

  const isProductPage =
    location.pathname.startsWith("/product/");

  const isCartPage =
    location.pathname === "/cart";

  const isSubPage =
    isProductPage || isCartPage;

  const cartCount =
    cart?.items.reduce(
      (total, item) => total + item.quantity,
      0
    ) ?? 0;

  const handleNavigation = (section: string) => {
    setMenuOpen(false);

    // Jesteśmy na stronie produktu lub koszyka
    if (isSubPage) {
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

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  return (
    <nav className="navbar">

      <button
        type="button"
        className="navbar__logo"
        onClick={() => handleNavigation("home")}
      >
        AI Cyber Store
      </button>

      <button
        type="button"
        className="navbar__menu-toggle"
        aria-expanded={menuOpen}
        aria-controls="primary-navigation"
        aria-label={menuOpen ? "Close navigation" : "Open navigation"}
        onClick={() => setMenuOpen((open) => !open)}
      >
        <span />
        <span />
        <span />
      </button>

      <div
        id="primary-navigation"
        className={`navbar__links${menuOpen ? " navbar__links--open" : ""}`}
      >

        <a
          className={
            !isProductPage &&
            !isCartPage &&
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
            !isCartPage &&
            activeSection === "recommendations"
              ? "active"
              : ""
          }
          onClick={() =>
            handleNavigation("recommendations")
          }
        >
          {t("nav.recommendations")}
        </a>

        <a
          className={
            isProductPage ||
            (!isCartPage &&
              activeSection === "shop")
              ? "active"
              : ""
          }
          onClick={() =>
            handleNavigation("shop")
          }
        >
          {t("nav.shop")}
        </a>

        <a
          className={
            isCartPage
              ? "active"
              : ""
          }
          onClick={() => {
            setMenuOpen(false);
            navigate("/cart");
          }}
        >
          {t("nav.cart")} ({cartCount})
        </a>

      </div>

      <LanguageSwitcher />

    </nav>
  );
}

export default Navbar;
