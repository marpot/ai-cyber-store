import {
  useEffect
} from "react";

import Hero from "@/components/Hero/Hero";
import RecommendationBox from "@/components/RecommendationBox/RecommendationBox";
import Shop from "@/components/Shop/Shop";

import {
  useScroll
} from "@/context/ScrollContext";

export default function Home() {

  const {
    setActiveSection
  } = useScroll();


  useEffect(() => {

    const scrollContainer =
      document.querySelector(
        ".page-scroll"
      );


    const sections =
      document.querySelectorAll(
        "section[id]"
      );


    if (!scrollContainer) {
      return;
    }


    const observer =
      new IntersectionObserver(

        (entries) => {

          entries.forEach(
            (entry) => {

              if (entry.isIntersecting) {

                const id =
                  entry.target.id;


                entry.target.classList.add(
                  "active"
                );


                setActiveSection(id);


                window.history.replaceState(
                  null,
                  "",
                  `#${id}`
                );

              }

            }
          );

        },

        {
          root: scrollContainer,
          threshold: 0.6,
        }

      );


    sections.forEach(
      (section) => {

        observer.observe(section);

      }
    );


    return () => {

      observer.disconnect();

    };


  }, [setActiveSection]);


  return (
    <>

      <Hero />

      <RecommendationBox />

      <Shop />

    </>
  );
}