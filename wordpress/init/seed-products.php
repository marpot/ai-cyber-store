<?php

if (!defined('ABSPATH')) {
    exit(1);
}

if (!class_exists('WooCommerce') || !class_exists('WC_Product_Simple')) {
    fwrite(STDERR, "WooCommerce must already be installed and active.\n");
    exit(1);
}

$products = [
    [
        'name' => 'SafeTunnel VPN',
        'slug' => 'safetunnel-vpn',
        'price' => '39.00',
        'category' => 'Network Security',
        'description' => 'A one-year VPN subscription that encrypts traffic on public Wi-Fi and protects browsing on laptops and phones.',
        'short' => 'Private, encrypted browsing on public Wi-Fi.',
        'recommended_for' => 'public Wi-Fi, travel, privacy, encrypted connection, remote work',
        'virtual' => true,
    ],
    [
        'name' => 'VaultPass Password Manager',
        'slug' => 'vaultpass-password-manager',
        'price' => '59.00',
        'category' => 'Identity & Access',
        'description' => 'A one-year password manager subscription with unique password generation, encrypted vaults and breach alerts.',
        'short' => 'Replace reused passwords with strong, unique credentials.',
        'recommended_for' => 'reused passwords, weak passwords, account security, credentials, secure sharing',
        'virtual' => true,
    ],
    [
        'name' => 'TitanKey Hardware Security Key',
        'slug' => 'titankey-hardware-security-key',
        'price' => '199.00',
        'category' => 'Identity & Access',
        'description' => 'A FIDO2/WebAuthn hardware security key for phishing-resistant multi-factor authentication on important accounts.',
        'short' => 'Physical two-factor protection for important accounts.',
        'recommended_for' => 'important accounts, MFA, 2FA, phishing resistance, account takeover',
        'virtual' => false,
    ],
    [
        'name' => 'Sentinel Endpoint Protection',
        'slug' => 'sentinel-endpoint-protection',
        'price' => '149.00',
        'category' => 'Endpoint Security',
        'description' => 'One year of malware, ransomware and suspicious-process protection for a work laptop or desktop computer.',
        'short' => 'Continuous protection for your work computer.',
        'recommended_for' => 'work computer, laptop, malware, ransomware, antivirus, endpoint monitoring',
        'virtual' => true,
    ],
    [
        'name' => 'CyberSafe Cloud Backup',
        'slug' => 'cybersafe-cloud-backup',
        'price' => '99.00',
        'category' => 'Data Protection',
        'description' => 'A one-year encrypted cloud backup plan with automatic versioning and recovery after loss or ransomware.',
        'short' => 'Encrypted, recoverable backups for essential files.',
        'recommended_for' => 'backup, important files, data loss, ransomware recovery, cloud storage',
        'virtual' => true,
    ],
];

foreach ($products as $data) {
    $existing = get_page_by_path($data['slug'], OBJECT, 'product');
    $product = $existing ? wc_get_product($existing->ID) : new WC_Product_Simple();

    if (!$product) {
        continue;
    }

    $product->set_name($data['name']);
    $product->set_slug($data['slug']);
    $product->set_status('publish');
    $product->set_catalog_visibility('visible');
    $product->set_description($data['description']);
    $product->set_short_description($data['short']);
    $product->set_regular_price($data['price']);
    $product->set_price($data['price']);
    $product->set_manage_stock(false);
    $product->set_stock_status('instock');
    $product->set_virtual($data['virtual']);

    $category = term_exists($data['category'], 'product_cat');

    if (!$category) {
        $category = wp_insert_term($data['category'], 'product_cat');
    }

    if (!is_wp_error($category)) {
        $category_id = is_array($category) ? $category['term_id'] : $category;
        $product->set_category_ids([(int) $category_id]);
    }

    $attribute = new WC_Product_Attribute();
    $attribute->set_name('Recommended for');
    $attribute->set_options([$data['recommended_for']]);
    $attribute->set_visible(true);
    $attribute->set_variation(false);
    $product->set_attributes([$attribute]);
    $product->save();
}
