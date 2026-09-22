<?php

/**
 * AI Cyber Store - CORS configuration
 */

/*
 * Zezwalamy frontendowi React/Vite na komunikację
 * z WordPress REST API.
 */
add_filter('allowed_http_origins', function ($origins) {

    $origins[] = 'http://localhost:5173';

    return array_unique($origins);
});


/*
 * Udostępniamy frontendowi nagłówki WooCommerce
 * potrzebne do obsługi koszyka.
 */
add_filter('rest_post_dispatch', function ($response) {

    if ($response instanceof WP_HTTP_Response) {

        $headers = $response->get_headers();

        if (isset($headers['Access-Control-Expose-Headers'])) {

            $existing =
                $headers['Access-Control-Expose-Headers'];

            $headersToExpose = array_map(
                'trim',
                explode(',', $existing)
            );

            if (!in_array('Nonce', $headersToExpose, true)) {
                $headersToExpose[] = 'Nonce';
            }

            if (!in_array('Cart-Token', $headersToExpose, true)) {
                $headersToExpose[] = 'Cart-Token';
            }

            $response->header(
                'Access-Control-Expose-Headers',
                implode(', ', $headersToExpose)
            );

        } else {

            $response->header(
                'Access-Control-Expose-Headers',
                'Nonce, Cart-Token'
            );
        }
    }

    return $response;
});


/*
 * Zwracamy kanoniczny URL natywnego checkoutu WooCommerce.
 * Dzięki temu frontend nie zależy od ID strony ani ustawień permalinków.
 */
add_action('rest_api_init', function () {
    register_rest_route('cyber-store/v1', '/checkout-url', [
        'methods' => 'GET',
        'permission_callback' => '__return_true',
        'callback' => function () {
            if (!function_exists('wc_get_checkout_url')) {
                return new WP_Error(
                    'woocommerce_unavailable',
                    'WooCommerce checkout is unavailable.',
                    ['status' => 503]
                );
            }

            return rest_ensure_response([
                'url' => wc_get_checkout_url(),
            ]);
        },
    ]);
});
