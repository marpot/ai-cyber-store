/* oxlint-disable react/only-export-components */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

interface CartImage {
  src: string;
  alt: string;
}

export interface CartItem {
  key: string;
  id: number;
  quantity: number;
  name: string;
  prices: {
    price: string;
    currency_code: string;
    currency_symbol: string;
  };
  images: CartImage[];
}

interface CartData {
  items: CartItem[];
  totals: {
    total_items: string;
    total_price: string;
    currency_code: string;
    currency_symbol: string;
  };
}

interface CartContextType {
  cart: CartData | null;
  loading: boolean;

  addToCart: (
    productId: number,
    quantity?: number
  ) => Promise<void>;

  updateQuantity: (
    key: string,
    quantity: number
  ) => Promise<void>;

  removeItem: (
    key: string
  ) => Promise<void>;

  refreshCart: () => Promise<void>;

  beginCheckout: () => Promise<void>;
}

const CartContext =
  createContext<CartContextType | undefined>(undefined);

export function CartProvider({
  children,
}: {
  children: ReactNode;
}) {
  const API_URL =
    import.meta.env.VITE_WP_API_URL || "http://localhost:8080";

  const [cart, setCart] =
    useState<CartData | null>(null);

  const [loading, setLoading] =
    useState(false);

  const getNonce = () => {
    return sessionStorage.getItem(
      "wc_cart_nonce"
    );
  };

  const saveNonce = (
    nonce: string | null
  ) => {
    if (nonce) {
      sessionStorage.setItem(
        "wc_cart_nonce",
        nonce
      );
    }
  };

  /*
   * Wspólna funkcja do komunikacji
   * z WooCommerce Store API.
   */

  const request = useCallback(async (
    endpoint: string,
    options: RequestInit = {}
  ) => {
    const nonce =
      getNonce();

    const headers =
      new Headers(options.headers);

    headers.set(
      "Content-Type",
      "application/json"
    );

    if (nonce) {
      headers.set(
        "Nonce",
        nonce
      );
    }

    console.log(
      "WooCommerce request:",
      {
        endpoint,
        method:
          options.method || "GET",
        nonce: nonce || null,
      }
    );

    const response =
      await fetch(
        `${API_URL}/wp-json/wc/store/v1/cart${endpoint}`,
        {
          ...options,
          headers,
          credentials: "include",
        }
      );

    /*
     * WooCommerce zwraca również Nonce.
     */

    const newNonce =
      response.headers.get(
        "Nonce"
      );

    console.log(
      "WooCommerce response headers:",
      {
        nonce:
          newNonce,
      }
    );

    saveNonce(
      newNonce
    );

    if (!response.ok) {
      const errorText =
        await response.text();

      throw new Error(
        `WooCommerce Cart API ${response.status}: ${errorText}`
      );
    }

    return response.json();
  }, [API_URL]);

  /*
   * Pobranie aktualnego koszyka.
   *
   * GET /cart
   *
   * Ten request również inicjalizuje
   * sesję WooCommerce oraz Nonce.
   */

  const refreshCart =
    useCallback(async () => {
      try {
        setLoading(true);

        const data =
          await request("");

        setCart(data);
      } catch (error) {
        console.error(
          "Cart loading error:",
          error
        );
      } finally {
        setLoading(false);
      }
    }, [request]);

  /*
   * Dodawanie produktu.
   *
   * WooCommerce wymaga Nonce przy POST.
   *
   * Jeżeli aplikacja jeszcze go nie posiada,
   * najpierw pobieramy /cart.
   */

  const addToCart = async (
    productId: number,
    quantity = 1
  ) => {
    try {
      setLoading(true);

      if (!getNonce()) {
        console.log(
          "No WooCommerce nonce found. Initializing cart..."
        );

        await request("");
      }

      console.log(
        "Adding product to cart:",
        {
          productId,
          quantity,
          nonce:
            getNonce(),
        }
      );

      const data =
        await request(
          `/add-item?id=${productId}&quantity=${quantity}`,
          {
            method: "POST",
          }
        );

      setCart(data);
    } catch (error) {
      console.error(
        "Add to cart error:",
        error
      );

      throw error;
    } finally {
      setLoading(false);
    }
  };

  /*
   * Zmiana ilości produktu.
   */

  const updateQuantity =
    async (
      key: string,
      quantity: number
    ) => {
      if (quantity <= 0) {
        await removeItem(key);
        return;
      }

      try {
        setLoading(true);

        if (!getNonce()) {
          await request("");
        }

        const data =
          await request(
            `/update-item?key=${encodeURIComponent(
              key
            )}&quantity=${quantity}`,
            {
              method: "POST",
            }
          );

        setCart(data);
      } catch (error) {
        console.error(
          "Update cart error:",
          error
        );

        throw error;
      } finally {
        setLoading(false);
      }
    };

  /*
   * Usunięcie produktu z koszyka.
   */

  const removeItem =
    async (
      key: string
    ) => {
      try {
        setLoading(true);

        if (!getNonce()) {
          await request("");
        }

        const data =
          await request(
            `/remove-item?key=${encodeURIComponent(
              key
            )}`,
            {
              method: "POST",
            }
          );

        setCart(data);
      } catch (error) {
        console.error(
          "Remove cart error:",
          error
        );

        throw error;
      } finally {
        setLoading(false);
      }
    };

  /*
   * Przejście do natywnego checkoutu WooCommerce.
   *
   * Koszyk Store API działa w tej samej sesji cookie, dzięki czemu
   * po przekierowaniu WooCommerce widzi te same produkty.
   */

  const beginCheckout = async () => {
    try {
      setLoading(true);

      const currentCart = await request("");

      setCart(currentCart);

      if (!currentCart.items?.length) {
        throw new Error("empty-cart");
      }

      const response = await fetch(
        `${API_URL}/wp-json/cyber-store/v1/checkout-url`,
        {
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error(
          `WooCommerce checkout URL ${response.status}`
        );
      }

      const data: { url?: string } = await response.json();

      if (!data.url) {
        throw new Error("missing-checkout-url");
      }

      const checkoutUrl = new URL(data.url, API_URL);

      if (!["http:", "https:"].includes(checkoutUrl.protocol)) {
        throw new Error("invalid-checkout-url");
      }

      window.location.assign(checkoutUrl.toString());
    } finally {
      setLoading(false);
    }
  };

  /*
   * Inicjalizacja koszyka
   * po uruchomieniu aplikacji.
   */

  useEffect(() => {
    refreshCart();
  }, [refreshCart]);

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        addToCart,
        updateQuantity,
        removeItem,
        refreshCart,
        beginCheckout,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context =
    useContext(CartContext);

  if (!context) {
    throw new Error(
      "useCart must be used inside CartProvider"
    );
  }

  return context;
}
