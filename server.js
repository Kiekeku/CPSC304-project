const express = require('express');
const appController = require('./appController');

const loadEnvFile = require('./utils/envUtil');
const envVariables = loadEnvFile('./.env');

const app = express();
const PORT = envVariables.PORT || 65534;

app.use(express.static('public'));
app.use(express.json());

app.use('/', appController);

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}/`);
});
