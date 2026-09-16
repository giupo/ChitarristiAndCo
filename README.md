# ChitarristiAndCo — Scaletta

Repertorio della band in `songs.csv` (editabile anche direttamente su GitHub). Ogni push su `main` che modifica `songs.csv` o `config.json` fa rigenerare automaticamente `setlist.pdf` tramite GitHub Actions, che lo pubblica come [Release](../../releases) scaricabile.

## File

- `songs.csv` — un brano per riga: `titolo, autore, tono_originale, tono_live, giro_accordi_1, giro_accordi_2, giro_special`. Usa `-` per una colonna vuota.
- `config.json` — titolo e sottotitolo (es. data della serata) mostrati in cima al PDF.
- `setlist.pdf` — il PDF generato, sempre lo stesso file (viene sovrascritto).
- `scripts/generate_pdf.py` — script che legge CSV + config e produce il PDF.

## Generare il PDF in locale

Richiede [uv](https://docs.astral.sh/uv/):

```bash
uv run scripts/generate_pdf.py
```
