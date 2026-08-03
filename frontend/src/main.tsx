import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";

import router from "./router";
import "./styles/main.scss";

import {
  ScrollProvider
} from "./context/ScrollContext";


createRoot(
  document.getElementById("root")!
).render(

  <StrictMode>

    <ScrollProvider>

      <RouterProvider router={router} />

    </ScrollProvider>

  </StrictMode>

);