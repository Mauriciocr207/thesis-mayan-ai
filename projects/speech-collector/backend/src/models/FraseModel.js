import pkg from 'pg';
const { Client } = pkg;

export class FraseModel {
    constructor(connString) {
        this.connString = connString;
    }

    async connect() {
        this.client = new Client({ connectionString: this.connString });
        await this.client.connect();
    }

    async close() {
        if (this.client) {
            await this.client.end();
        }
    }

    // ----------------------------------------
    // GET ALL PHRASES
    // ----------------------------------------
    async getAll() {
        try {
            await this.connect();
            const result = await this.client.query(`SELECT * FROM phrases`);
            return result.rows;
        } catch (e) {
            console.error("Error getting users:", e);
            throw e;
        } finally {
            await this.close();
        }
    }
}
