FROM node:18-alpine

# set working directory
WORKDIR /app

# copy package files
COPY package*.json ./

# install dependencies
RUN npm install

# copy source code
COPY . .

# expose port
EXPOSE 3000

# start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
