import "@/i18n/config";

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";

import router from "./router";
import "./styles/main.scss";

import {
  ScrollProvider,
} from "./context/ScrollContext";

import {
  CartProvider,
} from "./context/CartContext";

createRoot(
  document.getElementById("root")!
).render(
  <StrictMode>
    <ScrollProvider>
      <CartProvider>
        <RouterProvider router={router} />
      </CartProvider>
    </ScrollProvider>
  </StrictMode>
);