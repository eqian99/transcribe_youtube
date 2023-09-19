import boto3
import json
import time
import uuid
from pydub import AudioSegment
import argparse
from yt_dlp import YoutubeDL
import requests 
import os 

def download_audio(youtube_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio',  
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

def upload_to_s3(filename, bucket_name):
    s3 = boto3.client('s3')
    s3.upload_file(filename, bucket_name, filename)
    return f"s3://{bucket_name}/{filename}"

def transcribe_audio(job_name, job_uri):
    transcribe = boto3.client('transcribe', region_name='us-west-1')  # specify the region
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': job_uri},
        MediaFormat='wav',
        LanguageCode='en-US',
        Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 10}
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        time.sleep(15)
    return status['TranscriptionJob']['Transcript']['TranscriptFileUri']

def get_text_from_transcription(transcript_uri):
    response = requests.get(transcript_uri)
    transcript = response.json()
    items = transcript['results']['items']
    turns = []
    current_speaker = None
    sentence = ""
    for item in items:
        if 'type' in item and item['type'] == 'pronunciation':
            if 'speaker_label' in item and current_speaker != item['speaker_label'] and sentence:
                turns.append({'speaker': current_speaker, 'content': sentence.strip()})
                sentence = ""
            current_speaker = item['speaker_label']
            sentence += " " + item['alternatives'][0]['content']
        elif 'type' in item and item['type'] == 'punctuation':
            sentence += item['alternatives'][0]['content']
    if sentence:
        turns.append({'speaker': current_speaker, 'content': sentence.strip()})
    return turns

def format_transcript(turns):
    formatted_transcript = ""
    for turn in turns:
        formatted_transcript += f"{turn['speaker']}: {turn['content']}\n"
    return formatted_transcript

def parse_audio(youtube_url, bucket_name="transcribe-youtube-distinct-speakers"):
    job_name = f"TranscribeJob-{uuid.uuid4()}"

    download_audio(youtube_url)
    job_uri = upload_to_s3("audio.wav", bucket_name)
    transcript_uri = transcribe_audio(job_name, job_uri)
    text = get_text_from_transcription(transcript_uri)

    return text



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcribe a YouTube video.')
    parser.add_argument('youtube_url', type=str, help='The URL of the YouTube video to transcribe.')
    
    args = parser.parse_args()
    text = parse_audio(args.youtube_url)

    print(text)

    formatted_text = format_transcript(text)

    prompt = "Test prompt"

    # Make the request to the Claude API
    response = requests.post(
        "https://api.anthropic.com/v1/complete",
        headers={"Authorization": f"Bearer {os.getenv('ANTHROPIC_API_KEY')}"},
        json={"prompt": f"\n\nHuman: {prompt}\n\nAssistant:"},
    )

    output = response.json()["text"]
    print(output)

