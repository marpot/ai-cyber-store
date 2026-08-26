import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import type { ReactNode } from "react";

type ScrollContextType = {
  activeSection: string;

  setActiveSection: (
    section: string
  ) => void;

  scrollTo: (
    id: string
  ) => void;
};

const ScrollContext =
  createContext<ScrollContextType | null>(null);

export function ScrollProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [
    activeSection,
    setActiveSection,
  ] = useState("home");

  /*
   * Obserwujemy sekcje znajdujące się
   * wewnątrz głównego kontenera scrollowania.
   *
   * Dzięki temu activeSection zmienia się
   * również podczas ręcznego przewijania strony.
   */
  useEffect(() => {
    const container =
      document.querySelector(
        ".page-scroll"
      ) as HTMLElement | null;

    if (!container) {
      console.warn(
        "Scroll container not found: .page-scroll"
      );

      return;
    }

    const sections =
      container.querySelectorAll<HTMLElement>(
        "section[id]"
      );

    if (!sections.length) {
      return;
    }

    const observer =
      new IntersectionObserver(
        (entries) => {
          const visibleSections =
            entries
              .filter(
                (entry) =>
                  entry.isIntersecting
              )
              .sort(
                (a, b) =>
                  b.intersectionRatio -
                  a.intersectionRatio
              );

          if (
            visibleSections.length > 0
          ) {
            const section =
              visibleSections[0]
                .target as HTMLElement;

            setActiveSection(
              section.id
            );
          }
        },
        {
          root: container,

          /*
           * Sekcja jest uznawana za aktywną,
           * gdy znajduje się w centralnej części
           * kontenera.
           */
          rootMargin:
            "-20% 0px -60% 0px",

          threshold: [
            0,
            0.25,
            0.5,
            0.75,
            1,
          ],
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
  }, []);

  const scrollTo = (
    id: string
  ) => {
    const container =
      document.querySelector(
        ".page-scroll"
      ) as HTMLElement | null;

    const section =
      document.getElementById(id);

    if (!container || !section) {
      console.warn(
        "Scroll target not found:",
        id
      );

      return;
    }

    /*
     * Każda sekcja jest bezpośrednim
     * dzieckiem .page-scroll.
     *
     * Dlatego używamy offsetTop zamiast
     * scrollIntoView().
     */

    container.scrollTo({
      top: section.offsetTop,
      behavior: "smooth",
    });
  };

  return (
    <ScrollContext.Provider
      value={{
        activeSection,
        setActiveSection,
        scrollTo,
      }}
    >
      {children}
    </ScrollContext.Provider>
  );
}

export function useScroll() {
  const context =
    useContext(ScrollContext);

  if (!context) {
    throw new Error(
      "useScroll must be inside ScrollProvider"
    );
  }

  return context;
}