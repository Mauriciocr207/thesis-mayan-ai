import pkg from 'pg';
const { Client } = pkg;

export class UserModel {
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
    // GET ALL USERS
    // ----------------------------------------
    async getAll() {
        try {
            await this.connect();
            const result = await this.client.query(`
            SELECT 
                u.*,
                CASE 
                    WHEN EXISTS (
                        SELECT 1 FROM recordings r 
                        WHERE r.user_id = u.id
                    ) THEN 'complete'
                    ELSE 'incomplete'
                END as status
            FROM users u 
            ORDER BY created_at DESC
        `);
            return result.rows;
        } catch (e) {
            console.error("Error getting users:", e);
            throw e;
        } finally {
            await this.close();
        }
    }

    // ----------------------------------------
    // GET ONE USER BY ID
    // ----------------------------------------
    async getUserById(id) {
        try {
            await this.connect();
            const result = await this.client.query(`SELECT * FROM users WHERE id = $1`, [id]);
            return result.rows[0] || null;
        } catch (e) {
            console.error("Error getting user:", e);
            throw e;
        } finally {
            await this.close();
        }
    }

    // ----------------------------------------
    // CREATE USER
    // ----------------------------------------
    async create({ nombre, edad, sexo, localidad, ambiente, contacto, observaciones }) {
        try {
            await this.connect();

            const query = `
        INSERT INTO users (nombre, edad, sexo, localidad, ambiente, contacto, observaciones)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *;
      `;

            const result = await this.client.query(query, [
                nombre,
                edad,
                sexo,
                localidad,
                ambiente,
                contacto,
                observaciones
            ]);

            return result.rows[0].id;

        } catch (e) {
            console.error("Error creating user:", e);
            throw e;
        } finally {
            await this.close();
        }
    }

    // ----------------------------------------
    // UPDATE USER
    // ----------------------------------------
    async update(id, updates) {
        try {
            await this.connect();

            const allowedFields = ["nombre", "edad", "genero", "localidad", "ambiente"];
            const fields = [];
            const values = [];
            let index = 1;

            for (const key of allowedFields) {
                if (updates[key] !== undefined) {
                    fields.push(`${key} = $${index}`);
                    values.push(updates[key]);
                    index++;
                }
            }

            if (fields.length === 0) return null;

            const query = `
        UPDATE users
        SET ${fields.join(", ")}
        WHERE id = $${index}
        RETURNING *;
      `;

            values.push(id);

            const result = await this.client.query(query, values);
            return result.rows[0] || null;

        } catch (e) {
            console.error("Error updating user:", e);
            throw e;
        } finally {
            await this.close();
        }
    }

    // ----------------------------------------
    // DELETE USER
    // ----------------------------------------
    async delete(id) {
        try {
            await this.connect();
            const res = await this.client.query(`DELETE FROM users WHERE id = $1`, [id]);
            return true;
        } catch (e) {
            console.error("Error deleting user:", e);
            throw e;
        } finally {
            await this.close();
        }
    }
}
