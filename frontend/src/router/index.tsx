import { createBrowserRouter } from "react-router-dom";

import MainLayout from "@/layouts/MainLayout";

import Home from "@/pages/Home";
import Product from "@/pages/Product/Product";
import Cart from "@/pages/Cart/Cart";


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
        path: "product/:id",
        element: <Product />,
      },

      {
        path: "cart",
        element: <Cart />,
      },

    ],

  },

]);


export default router;