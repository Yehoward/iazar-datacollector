# İAZAR strîngător de date

Este un strîngător date (audio) pentru antrenarea modelului nostru de transcrierea vocii în text.

# Instalare 

Clonați repozitoriul:

```sh 
git clone https://github.com/Yehoward/iazar-datacollector.git

```

Instalați (în mediu virtual):

```sh
pipenv install
```

Veți avea nevoie de un [telegram jeton(token)](https://core.telegram.org/bots/tutorial#obtain-your-bot-token).
Care-l plasați în fișierul `.env`

```sh
KEY="Cheia-voastră"
```
Derulați botul (în mediu virtual):

```sh
pipenv run python bot.py
```

Derulați programul pentru colectare:

```sh
pipenv run python cli.py
```

# Operare


```
dataset/
├── data/
│   ├── 2024-04-29T14:20:44.wav
│   └── tg-2024-04-30T11:22:21.wav
├── metadata.csv
└── nevalidate.csv

```

> [!IMPORTANT]
>
> În fișierele `.csv` trebuie să scrieți coloanele `file_name,transcription`


## Bot telegram

Salvează datele la calea `dataset/data/`, și descripția în fișierul `nevalidate.csv`.


## Linia de comandă

Salvează datele la calea `dataset/data/`, și descripția în fișierul `metadata.csv`.

## Gruparea datelor

`split_data.fish` este un script scris în [fish](https://fishshell.com/) pentru împărțirea datelor în directorii(train și test).
Pentru antrenarea modelului avem nevoie numai de acestea grupe de date.[^hugging_split]

#### proces de împărțire

- Validăm audiourile din `nevalidate.csv` și le transcriem în `metadata.csv`.


- Împărțim datele din fișierul `metadata.csv`.
Scriptul împarte datele în funcțiile de căile menționate în `metadata.csv`.


```csv
file_name,transcription
data/2024-04-29T14:20:44.wav
data/tg-2024-04-30T11:22:21.wav
```
Specificăm audiourile în părțile care dorim, modificînd calea în `metadata.csv`.

```csv
file_name,transcription
data/train/2024-04-29T14:20:44.wav
data/test/tg-2024-04-30T11:22:21.wav

```

- Derulăm scriptul:

```sh
./split_data.fish
```

## Postarea datelor

Datele le postăm pe repozitoriu de la [HuggingFace](https://huggingface.co) cu
ajutorul unui script simplu `push_data.py`.[^hugging_audio_folder].

În cazul nostru datele au fost plasate pe un repozitoriu privat.

---
[^hugging_audio_folder]: https://huggingface.co/docs/datasets/audio_dataset#audiofolder
[^hugging_split]: https://huggingface.co/docs/datasets/repository_structure#split-pattern-hierarchy


