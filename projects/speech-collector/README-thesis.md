# speech-collector en este repositorio

Fork de [`neuralwork/sound-collector`](https://github.com/neuralwork/sound-collector) (MIT),
la app web con la que se recogieron las grabaciones propias del corpus (`spk_014`–`spk_018`,
hoy en `data/source/recordings/`). El README original de upstream está en
[README.md](README.md).

**No está en uso activo.** Se conserva porque documenta cómo se recogió esa parte del corpus.

```bash
cd projects/speech-collector && pnpm i && pnpm dev
```

Necesita PostgreSQL y un `.env` (ver `docs/database-setup.md`). Ni `.env` ni `node_modules/`
ni `sound_recordings/` se versionan.
