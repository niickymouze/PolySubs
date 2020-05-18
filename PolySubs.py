import ffmpeg
import base64
import os
import datetime
import srt
import random
from google.cloud import speech_v1
from google.cloud import storage
from google.cloud import translate_v2 as translate
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="config/credentials.json"

# Upload to Cloud Storage
def upload_audio(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

def sample_recognize(storage_uri):
    """
    Transcribe a short audio file from Cloud Storage using a specified
    transcription model

    Args:
      storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
      model The transcription model to use, e.g. video, phone_call, default
      For a list of available transcription models, see:
      https://cloud.google.com/speech-to-text/docs/transcription-model#transcription_models
    """

    client = speech_v1.SpeechClient()

    config = {"model": "video", "language_code": "en-US", "encoding": "FLAC", "enable_word_time_offsets": True, "enable_automatic_punctuation": True}
    audio = {"uri": storage_uri}

    response = client.recognize(config, audio)
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
    return response.results

def translate_text_es(text, target='') :
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language='es')
    return result


def translate_text_ru(text, target='') :
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language='ru')
    return result


def translate_text_ja(text, target='') :
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language='ja')
    return result

def generate_srt(response, bin_size=3):
    transcriptions = []
    index = 0
    for result in res:
        try:
            # Start time of bin
            if result.alternatives[0].words[0].start_time.seconds:
                start_second = result.alternatives[0].words[0].start_time.seconds
                start_microsecond = result.alternatives[0].words[0].start_time.nanos * 0.001
            elif result.alternatives[0].words[0].start_time.seconds:
                start_second = 0
                start_microsecond = result.alternatives[0].words[0].start_time.nanos * 0.001
            else:
                start_second = 0
                start_microsecond = 0
            # End time of bin
            end_second = start_second + bin_size
            # End time of sentence
            tail_end_second = result.alternatives[0].words[-1].end_time.seconds
            tail_end_microsecond = result.alternatives[0].words[-1].end_time.nanos * 0.001
            bin_transcript = ''
            for i in range(len(result.alternatives[0].words)):
                try:
                    word = result.alternatives[0].words[i].word
                    word_start_second = result.alternatives[0].words[i].start_time.seconds
                    word_start_microsecond = result.alternatives[0].words[i].start_time.nanos * 0.001
                    word_end_second = result.alternatives[0].words[i].end_time.seconds
                    word_end_microsecond = result.alternatives[0].words[i].end_time.nanos * 0.001
                    if word_end_second < end_second:
                        bin_transcript = bin_transcript + " " + word
                    elif index > 0:
                        prev_word_end_second = result.alternatives[0].words[i-1].end_time.seconds
                        prev_word_end_microsecond = result.alternatives[0].words[i-1].end_time.nanos * 0.001
                        rand = random.randrange(1, 100)
                        if(rand > 25 and rand < 50):
                            sub = translate_text_es(bin_transcript)
                            bin_transcript = sub['translatedText']
                            transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_second, start_microsecond), datetime.timedelta(0,prev_word_end_second, prev_word_end_microsecond), bin_transcript))
                        elif(rand > 50 and rand < 75):
                            sub = translate_text_ru(bin_transcript)
                            bin_transcript = sub['translatedText']
                            transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_second, start_microsecond), datetime.timedelta(0,prev_word_end_second, prev_word_end_microsecond), bin_transcript))
                        elif(rand > 75 and rand < 100):
                            sub = translate_text_ja(bin_transcript)
                            bin_transcript = sub['translatedText']
                            transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_second, start_microsecond), datetime.timedelta(0,prev_word_end_second, prev_word_end_microsecond), bin_transcript))
                        else:
                            transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_second, start_microsecond), datetime.timedelta(0,prev_word_end_second, prev_word_end_microsecond), bin_transcript))
                        start_second = word_start_second
                        start_microsecond = word_start_microsecond
                        end_second = start_second + bin_size
                        bin_transcript = result.alternatives[0].words[i].word
                        index += 1
                except IndexError:
                    pass
            rand2 = random.randrange(1, 100)
            if(rand2 > 25 and rand2 < 50):
                sub = translate_text_es(bin_transcript)
                bin_transcript = sub['translatedText']
                transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_second, start_microsecond), datetime.timedelta(0, tail_end_second, tail_end_microsecond), bin_transcript))
            elif(rand2 > 50 and rand2 < 75):
                sub = translate_text_ja(bin_transcript)
                bin_transcript = sub['translatedText']
                transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_second, start_microsecond), datetime.timedelta(0, tail_end_second, tail_end_microsecond), bin_transcript))
            else:
                 transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_second, start_microsecond), datetime.timedelta(0, tail_end_second, tail_end_microsecond), bin_transcript))
            index += 1
        except IndexError:
            pass
    # turn transcription list into subtitles
    subtitles = srt.compose(transcriptions)
    with open("subtitles.srt","w") as f:
        f.write(subtitles)

def main():
    # Clear files
    if os.path.exists('audio.flac'):
        os.remove('audio.flac')
    if os.path.exists('script.txt'):
        os.remove('script.txt')

    # Convert Video to Audio
    video_input = ffmpeg.input('demo/despacito.mp4')
    video_audio = video_input.audio
    out = ffmpeg.output(video_audio, 'audio.flac', ac=1)
    out.run()

    # Upload Audio to Google Cloud
    while not os.path.exists('audio.flac'):
    time.sleep(2)
    upload_audio("polysubs","audio.flac","audio.flac")

    # Run Google speech to text model
    res = sample_recognize("gs://polysubs/audio.flac")
    with open('script.txt','w') as f:
        f.write(str(res))

    # Create subtitles.srt file
    while not os.path.exists('script.txt'):
        time.sleep(2)
    try :
        generate_srt(res)
    except:
        print('Something went wrong generating subtitles')

if __name == '__main__':
    main()
