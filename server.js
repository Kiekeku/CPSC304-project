const express = require('express');
const appController = require('./appController');

const loadEnvFile = require('./utils/envUtil');
const envVariables = loadEnvFile('./.env');

const app = express();
const PORT = envVariables.PORT || 65534;

app.use(express.static('frontend/dist'));
app.use(express.json());

app.use('/', appController);

app.get('*', (req, res) => {
    res.sendFile('index.html', { root: 'frontend/dist' });
});

app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}/`);
});

