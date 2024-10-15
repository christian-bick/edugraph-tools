FROM node:22.9.0

ENV NODE_ENV=development

WORKDIR /usr/src/app

RUN --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    --mount=type=cache,target=/root/.npm \
    npm ci

ENV PATH=/usr/src/app/node_modules/.bin:$PATH

COPY *.js *.html *.scss *.json /usr/src/app/
COPY /styles /usr/src/app/styles/

EXPOSE 3000

CMD npm run dev