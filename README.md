# ChitarristiAndCo — Scaletta

Repertorio della band in `songs.csv` (editabile anche direttamente su GitHub). Ogni push su `main` che modifica `songs.csv` o `config.json` fa rigenerare automaticamente `setlist.pdf` tramite GitHub Actions, che lo pubblica come [Release](../../releases) scaricabile.

## File

- `songs.csv` — il database di tutto il repertorio, un brano per riga: `id, titolo, autore, tono_originale, tono_live, giro_accordi_1, giro_accordi_2, giro_special`. `id` è un progressivo univoco (non riutilizzare un id dopo aver tolto un brano). Usa `-` per una colonna vuota.
- `config.json` — titolo e sottotitolo mostrati in cima al PDF, più `song_ids`: l'elenco ordinato degli `id` da includere nella scaletta. Per fare una nuova scaletta basta cambiare questa lista (selezione e ordine), senza toccare `songs.csv`.
- `setlist.pdf` — il PDF generato, sempre lo stesso file (viene sovrascritto).
- `scripts/generate_pdf.py` — script che legge il DB, seleziona i brani in `song_ids` e produce il PDF.

## Generare il PDF in locale

Richiede [uv](https://docs.astral.sh/uv/):

```bash
uv run scripts/generate_pdf.py
```
