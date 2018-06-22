FROM camptocamp/c2cwsgiutils:2
MAINTAINER Stéphane Brunner <stephane.brunner@camptocamp.com>

RUN \
  apt-get update && \
  apt-get install --assume-yes --no-install-recommends \
    ca-certificates \
    libmapnik-dev \
    mapnik-utils \
    gdal-bin \
    libdb-dev \
    fonts-dejavu \
    node-carto \
    osm2pgsql \
    curl \
    unzip && \
  cd /tmp && \
  mkdir /fonts && \
  mkdir /project && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache/* \
  adduser www-data root

COPY requirements.txt /app/

RUN \
  cd /app && \
  pip install --no-cache-dir -r requirements.txt

ENV TILEGENERATION_CONFIGFILE=/etc/tilegeneration/config.yaml \
    C2CWSGI_LOG_LEVEL=WARN \
    TILECLOUD_LOG_LEVEL=INFO \
    TILECLOUD_CHAIN_LOG_LEVEL=INFO \
    GUNICORN_PARAMS="--bind=:80 --worker-class=gthread --threads=10 --workers=5 --worker-connections=1000" \
    VISIBLE_ENTRY_POINT=/tiles/

EXPOSE 80

WORKDIR /etc/tilegeneration/

COPY . /app/

RUN \
  cd /app && \
  pip install --editable=. && \
  mv docker/run /usr/bin/
