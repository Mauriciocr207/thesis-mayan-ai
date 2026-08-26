import express from 'express';
import cors from 'cors';
import multer from 'multer';
import pkg from 'pg';

import { FileStorage } from './fileStorage.js';
import { UserController } from './controllers/UserController.js';
import { FraseController } from './controllers/FraseController.js';

const password = encodeURIComponent(process.env.PG_PASSWORD);
const connString = `postgresql://${process.env.PG_USER}:${password}@${process.env.PG_HOST}:${process.env.PG_PORT}/${process.env.PG_DATABASE}`;
const fileStorage = new FileStorage(process.env.STORAGE);

// Express app setup
const app = express();
app.use(cors({ origin: process.env.APP_URL }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
const upload = multer();


// Routes
app.get('/api/get-users', UserController.getAllUsers);
app.post('/api/add-user', UserController.createUser);
app.get('/api/get-user', UserController.getUser);
app.delete('/api/delete-user', UserController.deleteUser);
app.get('/api/get-phrases', FraseController.getAllPhrases);

app.post('/api/upload-sound', upload.single('file'), async (req, res) => {
  const { username, taskId } = req.body;
  const file = req.file;
  try {
    await fileStorage.saveRecording(file, taskId + '.wav');
    const { success } = await provider.submitTask(taskId);
    res.json({
      success: success
    });
  } catch (error) {
    console.log(error.message)
    res.json({
      success: false,
      error: "Internal server error."
    });
  }
});

app.post('/api/update-user-metadata', async (req, res) => {
  const { Client } = pkg;
  const client = new Client({
    connectionString: connString,
  });
  const { username, metadata } = req.body;
  try {
    await client.connect();
    if (!username) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    await client.query(`
      UPDATE users
      SET metadata=$1
      WHERE username=$2
    `, [metadata, username]);

    res.status(201).json({ message: 'User metadata updated successfully' });
  } catch (error) {
    const errMessage = `Error updating user ${username}` + error;
    console.log(errMessage);
    res.status(500).json({ error: errMessage });
  } finally {
    await client.end();
  }
});

app.get('/ping', (req, res) => {
  res.json({ ready: true });
});

app.listen(8000, () => {
  console.log('Server is running on port 8000');
});
