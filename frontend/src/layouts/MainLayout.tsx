import { Outlet } from "react-router-dom";
import Navbar from "@/components/Navbar/Navbar";
// import Footer from "@/components/Footer/Footer";

export default function MainLayout() {
  return (
    <>
      <Navbar />

      <main className="page-scroll">
        <Outlet />
      </main>

      {/* <Footer /> */}    </>
  );
}