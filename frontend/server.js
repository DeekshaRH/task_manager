const express = require('express');
const axios = require('axios');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const API_URL = process.env.API_URL || 'http://localhost:8000';

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Routes
app.get('/', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/api/tasks`);
        const statsResponse = await axios.get(`${API_URL}/api/stats`);
        res.render('index', { 
            tasks: response.data,
            stats: statsResponse.data
        });
    } catch (error) {
        console.error('Error fetching tasks:', error.message);
        res.render('index', { 
            tasks: [],
            stats: { total: 0, pending: 0, in_progress: 0, completed: 0 }
        });
    }
});

app.get('/api/tasks', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/api/tasks`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/tasks', async (req, res) => {
    try {
        const response = await axios.post(`${API_URL}/api/tasks`, req.body);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.put('/api/tasks/:id', async (req, res) => {
    try {
        const response = await axios.put(`${API_URL}/api/tasks/${req.params.id}`, req.body);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.delete('/api/tasks/:id', async (req, res) => {
    try {
        const response = await axios.delete(`${API_URL}/api/tasks/${req.params.id}`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.get('/api/stats', async (req, res) => {
    try {
        const response = await axios.get(`${API_URL}/api/stats`);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Frontend server running on http://localhost:${PORT}`);
});
