FROM node:22.9.0

ENV NODE_ENV=development
ARG APP_DIR="/usr/src/app"

WORKDIR $APP_DIR

RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    --mount=type=cache,target=/root/.npm \
    npm ci

ENV PATH=$APP_DIR/node_modules/.bin:$PATH

COPY *.js *.html *.scss *.json $APP_DIR/
COPY /styles $APP_DIR/styles/
COPY /scripts $APP_DIR/scripts/
COPY /public $APP_DIR/public/

EXPOSE 3000

CMD ["npm", "run", "dev"]
