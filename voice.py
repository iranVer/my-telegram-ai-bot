import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)


def voice_to_text(file_path):
    with open(file_path, "rb") as audio_file:

        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    return result.text


def text_to_voice(text, output_path):
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=text
    ) as response:

        response.stream_to_file(output_path)

    return output_path
