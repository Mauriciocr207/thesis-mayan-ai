import pkg from 'pg';
import { FraseModel } from '../models/FraseModel.js';

const password = encodeURIComponent(process.env.PG_PASSWORD);
const connString = `postgresql://${process.env.PG_USER}:${password}@${process.env.PG_HOST}:${process.env.PG_PORT}/${process.env.PG_DATABASE}`;
const fraseModel = new FraseModel(connString);

export class FraseController {
    static async getAllPhrases(req, res) {
        try {
            const result = await fraseModel.getAll();
            // If not successful, send the failure message and a relevant status code
            res.status(200).json(result);
        } catch (error) {
            console.error("Error in /get-task endpoint:", error);
            res.status(500).json({ success: false, message: 'An internal server error occurred' });
        }
    }
}