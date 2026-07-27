FROM node:22

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

COPY docker-entrypoint.sh .

RUN chmod +x docker-entrypoint.sh

EXPOSE 5173

ENTRYPOINT ["./docker-entrypoint.sh"]