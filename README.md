# PolySubs
Multilingual subtitle generator using Google's Speech to Text and Translation models
<br /> Inspired by TerribleHacks 2020

## Description
> Learn new languages while watching your favourite videos!
<br />Polysubs generates subtitle for your videos with each block in a different language.

>Video Languages Supported: English
<br /> Subtitle Languages Supported: English, Spanish, Russian, Japanese

## Demo

![Demo_Gif](demo/demo.gif)

Generation Process:
1. Convert the video to an audio format
2. Upload audio to Google Cloud Bucket for storage / analysis (Necessary for larger files)
3. Run Google's Speech to Text model to generate a subtitle file in English
4. Run Google's Translation model to translate subtitles into numerous languages
