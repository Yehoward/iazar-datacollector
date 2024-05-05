#!/usr/bin/env fish
for audio_data in $(grep "train" ./dataset/metadata.csv)
    set name $(echo $audio_data | cut -d "," -f 1 | cut -d "/" -f 3)
    echo $name

    mv ./dataset/data/$name ./dataset/data/train/
end

mv dataset/data/*.wav dataset/data/test/
