from pathlib import Path

from datasets import DatasetDict, load_dataset


def push(dataset):
    dataset.push_to_hub("Yehoward/iazar-date", private=True)


def main():
    path = Path().cwd() / "dataset"
    data_set = load_dataset("audiofolder", data_dir=str(path))
    push(data_set)

if __name__ == "__main__":
    main()
