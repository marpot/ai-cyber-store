import { createBrowserRouter } from "react-router-dom";

import MainLayout from "@/layouts/MainLayout";

import Home from "@/pages/Home";
import Shop from "@/pages/Shop";
import Product from "@/pages/Product";

const router = createBrowserRouter([
  {
    path: "/",
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Home />,
      },
      {
        path: "shop",
        element: <Shop />,
      },
      {
        path: "product/:id",
        element: <Product />,
      },
    ],
  },
]);

export default router;