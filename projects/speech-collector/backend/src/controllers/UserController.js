import pkg from 'pg';
import { UserModel } from '../models/UserModel.js';

const password = encodeURIComponent(process.env.PG_PASSWORD);
const connString = `postgresql://${process.env.PG_USER}:${password}@${process.env.PG_HOST}:${process.env.PG_PORT}/${process.env.PG_DATABASE}`;
const userModel = new UserModel(connString);

export class UserController {
    static async getAllUsers(req, res) {
        const { username } = req.body;
        try {
            const result = await userModel.getAll(username);
            // If not successful, send the failure message and a relevant status code
            res.status(200).json(result);
        } catch (error) {
            console.error("Error in /get-task endpoint:", error);
            res.status(500).json({ success: false, message: 'An internal server error occurred' });
        }
    }

    static async createUser(req, res) {
        const { Client } = pkg;
        const client = new Client({
            connectionString: connString,
        });

        try {
            await client.connect();

            // Extract user data from the request body
            const {
                nombre,
                edad,
                sexo,
                localidad,
                ambiente,
                contacto,
                observaciones,
            } = req.body;

            // Basic validation (add more as needed)
            if (!nombre || !edad || !sexo || !localidad || !ambiente || !contacto) {
                return res.status(400).json({ error: 'Missing required fields' });
            }

            // Insert user into the database
            const id = await userModel.create({
                nombre,
                edad,
                sexo,
                localidad,
                ambiente,
                contacto,
                observaciones,
            });

            if (!id) {
                return res.status(500).json({ error: 'Failed to add user' });
            }

            res.status(201).json({ status: 'User added successfully', id });
        } catch (error) {
            console.error('Error adding user:', error);
            res.status(500).json({ error: 'An error occurred while adding the user' });
        } finally {
            await client.end();
        }
    }

    static async getUser(req, res) {
        const { userId } = req.query;
        try {
            const user = await userModel.getUserById(userId);
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
            res.status(200).json(user);
        } catch (error) {
            console.error("Error in /get-user endpoint:", error);
            res.status(500).json({ success: false, message: 'An internal server error occurred' });
        }
    }

    static async deleteUser(req, res) {
        const { id } = req.body;
        try {
            const deleted = await userModel.delete(id);
            res.status(200).json({ deleted });
        } catch (error) {
            console.error("Error in /get-user endpoint:", error);
            res.status(500).json({ success: false, message: 'An internal server error occurred' });
        }
    }
}