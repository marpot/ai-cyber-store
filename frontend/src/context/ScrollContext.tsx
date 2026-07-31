import {
  createContext,
  useContext,
  useState,
  ReactNode,
} from "react";


type ScrollContextType = {
  activeSection: string;
  setActiveSection: (section: string) => void;
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


  return (
    <ScrollContext.Provider
      value={{
        activeSection,
        setActiveSection,
      }}
    >
      {children}
    </ScrollContext.Provider>
  );
}



export function useScroll() {

  const context = useContext(ScrollContext);


  if (!context) {
    throw new Error(
      "useScroll must be inside ScrollProvider"
    );
  }


  return context;
}