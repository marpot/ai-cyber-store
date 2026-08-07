import { useTranslation } from "react-i18next";
import { useScroll } from "@/context/ScrollContext";

import "@/components/Hero/Hero.scss";

export default function Hero() {

  const {
    t
  } = useTranslation();


  const {
    scrollTo
  } = useScroll();


  return (

    <section
      id="home"
      className="hero"
    >

      <div className="hero__content">


        <h1>
          {t("hero.title")}
        </h1>


        <h2>
          {t("hero.subtitle")}
        </h2>


        <p>
          {t("hero.description")}
        </p>


        <button
          onClick={() => scrollTo("shop")}
        >
          {t("hero.button")}
        </button>


      </div>

    </section>

  );

}