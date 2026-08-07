import {
  createContext,
  useContext,
  useState,
} from "react";

import type { ReactNode } from "react";


type ScrollContextType = {

  activeSection: string;

  setActiveSection: (section: string) => void;

  scrollTo: (id: string) => void;

};



const ScrollContext =
  createContext<ScrollContextType | null>(null);




export function ScrollProvider({
  children,
}: {
  children: ReactNode;
}) {


  const [activeSection, setActiveSection] =
    useState("home");



  const scrollTo = (
    id: string
  ) => {

    document
      .getElementById(id)
      ?.scrollIntoView({
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