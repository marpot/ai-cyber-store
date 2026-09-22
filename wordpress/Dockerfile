FROM wordpress:latest

ARG WOOCOMMERCE_VERSION=11.1.1

RUN a2enmod headers

RUN set -eux; \
    curl -fsSL \
        "https://downloads.wordpress.org/plugin/woocommerce.${WOOCOMMERCE_VERSION}.zip" \
        -o /tmp/woocommerce.zip; \
    php -r '$archive = new ZipArchive(); $archive->open("/tmp/woocommerce.zip"); $archive->extractTo("/usr/src/wordpress/wp-content/plugins"); $archive->close();'; \
    rm /tmp/woocommerce.zip

COPY apache/000-default.conf /etc/apache2/sites-enabled/000-default.conf
