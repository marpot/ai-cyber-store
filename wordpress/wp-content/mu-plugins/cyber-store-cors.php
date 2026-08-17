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