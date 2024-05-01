from subprocess import Popen
from pathlib import Path
from datetime import datetime
from tempfile import NamedTemporaryFile
import csv
import os

from transformers import pipeline


def info(msg) -> None:
    print("info:",msg)

info("se încarcă modelul")
pipe = pipeline(model="Yehoward/whisper-small-ro")
info("model încărcat")



def record_audio(directory: Path) -> str | None:  

    if not directory.exists():
        raise FileNotFoundError(f"Nu există acest directoriu: {directory}")

    name = datetime.now().isoformat(timespec="seconds")
    file_path = f"{directory}/{name}.wav"
    ffmpeg_cmd: list =  f"ffmpeg -f alsa -i hw:0 -b:a 32k -ar 16000 {file_path}" .split()
    
    with Popen(ffmpeg_cmd) as proc:
        try:
            proc.wait()
        except KeyboardInterrupt:
            info("ștergem fișierul")
            os.remove(file_path)
            return

    return file_path

def transcribe(audio_path: str):
    info("se transcrie")
    return pipe(audio_path)["text"]

def edit_text(text, paf):
    with NamedTemporaryFile("r+", suffix=".md") as f:
        f.write(text)
        f.flush()
        with Popen(["nvim", "-c", f"nmap <leader>m :!mpv --really-quiet {paf}", f.name]) as proc:
            code = proc.wait()
            
        with open(f.name) as f:
            if new_text := f.read().strip():
                return new_text

    return text



def main():

    path = Path().cwd() / "dataset"
    path_to_audios = path / "data"
    audio_path = record_audio(path_to_audios)

    if audio_path is None:
        rasp = input("Ieș?: Y:n")
        if rasp.lower() == 'n':
            main()
        return


    text = transcribe(audio_path)
    print(text)

    ras = input("Modifică textul?: D/n")

    if ras.lower() != 'n':
        text = edit_text(text, audio_path)

    print(text)

    csv_path = path / "metadata.csv"

    with open(csv_path, "a") as f:
        info("salvăm datele in csv")
        data = csv.DictWriter(f, ["file_name", "transcription"])
        data_paf = "/".join(str(audio_path).split("/")[-2:])
        data.writerow({'file_name': data_paf, 'transcription': text})

    info("datele-s salvate")




if __name__ == "__main__":
    main()

