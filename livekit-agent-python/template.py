from google.cloud import speech
from google.cloud import texttospeech

from livekit.agents.stt import STT, STTStream, STTEvent
from google.cloud import speech


class GCP_STT(STT):
    def __init__(self, language="en-IN"):
        super().__init__()
        self.language = language
        self.client = speech.SpeechClient()

        class Cap:
            streaming = False
        self.capabilities = Cap()

    async def stream(self) -> STTStream:
        return GCPStream(self.client, self.language)


class GCPStream(STTStream):
    def __init__(self, client, language):
        super().__init__()
        self.client = client
        self.language = language
        self.buffer = bytearray()
        self._closed = False

    async def write(self, frame):
        self.buffer.extend(frame.data)

    async def close(self):
        self._closed = True

    async def __anext__(self):
        if not self._closed:
            raise StopAsyncIteration

        audio = speech.RecognitionAudio(content=bytes(self.buffer))

        config = speech.RecognitionConfig(
            language_code=self.language,
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
        )

        response = self.client.recognize(config=config, audio=audio)

        text = ""
        if response.results:
            text = response.results[0].alternatives[0].transcript

        return STTEvent(
            type="transcript",
            text=text,
            final=True
        )



class GCP_TTS:
    def __init__(self, voice="en-IN-Standard-B"):
        self.voice = voice
        self.client = texttospeech.TextToSpeechClient()

    async def synthesize(self, text: str) -> bytes:
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice_params = texttospeech.VoiceSelectionParams(
            language_code="en-IN",
            name=self.voice,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            sample_rate_hertz=24000,
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config,
        )

        return response.audio_content