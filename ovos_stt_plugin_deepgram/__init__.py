import json
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import speech_recognition as sr
from ovos_plugin_manager.templates.stt import STT


class Recognizer(sr.Recognizer):
    # port of https://github.com/Uberi/speech_recognition/pull/631

    def recognize_deepgram(
            self,
            audio_data,
            key,
            tier='enhanced',
            model='general',
            version='latest',
            language='en-US',
            detect_language=False,
            punctuate=True,
            profanity_filter=False,
            redact=None,
            diarize=False,
            diarize_version=None,
            ner=True,
            multichannel=False,
            alternatives=1,
            numerals=True,
            search=None,
            replace=None,
            keywords=None,
            paragraphs=False,
            summarize=False,
            detect_topics=False,
            utterances=False,
            utt_split=None,
            show_all=False
    ):
        """
        Performs speech recognition of ``audio_data`` (an ``AudioData`` instance) using the Deepgram speech recognition API.
        Deepgram uses an API secret to authenticate users and authorize requests. To obtain an API secret, create an account with `Deepgram <https://console.deepgram.com>`__. The API secret is a 40-character hexadecimal string that can only be retrieved at creation time. It is identified using a UUID, which is not the API secret and shouldn't be used here.
        If ``show_all`` is false (the default), returns the most likely transcript string; otherwise, returns the raw API JSON response.
        Details of the various features can be found in the `Deepgram Documentation <https://developers.deepgram.com/>`__.
        """
        assert isinstance(audio_data, sr.AudioData), "``audio_data`` must be audio data"
        assert isinstance(key, str), "``key`` must be a string"
        assert tier is None or (isinstance(tier, str) and tier in {'base', 'enhanced'}), "invalid ``tier``"
        assert model is None or isinstance(model, str), "``model`` must be None or a string"
        assert version is None or isinstance(version, str), "``verison`` must be None or a string"
        assert language is None or isinstance(language, str), "``language`` must be None or a string"
        assert isinstance(detect_language, bool), "``detect_language`` must be a bool"
        assert isinstance(punctuate, bool), "``punctuate`` must be a bool"
        assert isinstance(profanity_filter, bool), "``profanity_filter`` must be a bool"
        assert redact is None or isinstance(redact, str), "``redact`` must be None or a string"
        assert isinstance(diarize, bool), "``diarize`` must be a bool"
        assert diarize_version is None or isinstance(diarize_version,
                                                     str), "``diarize_version`` must be None or a string"
        assert isinstance(ner, bool), "``ner`` must be a bool"
        assert isinstance(multichannel, bool), "``multichannel`` must be a bool"
        assert isinstance(alternatives, int) and alternatives > 0, "``alternatives`` must be a positive integer"
        assert isinstance(numerals, bool), "``numerals`` must be a bool"
        assert search is None or (isinstance(search, list) and all(
            isinstance(s, str) for s in search)), "``search`` must be None or a list of strings"
        assert replace is None or (isinstance(replace, dict) and all(
            isinstance(k, str) and isinstance(v, str) for k, v in
            replace.items())), "``replace`` must be None or a dicitonary with string keys and values"
        assert keywords is None or (isinstance(keywords, list) and all(
            isinstance(s, str) for s in keywords)), "``keywords`` must be None or a list of strings"
        assert isinstance(paragraphs, bool), "``paragraphs`` must be a bool"
        assert isinstance(summarize, bool), "``summarize`` must be a bool"
        assert isinstance(detect_topics, bool), "``detect_topics`` must be a bool"
        assert isinstance(utterances, bool), "``utterances`` must be a bool"
        assert utt_split is None or (isinstance(utt_split, (
            int, float)) and utt_split > 0), "``utt_split`` must be None or positive real number"

        def convert_bool(x):
            if isinstance(x, bool):
                return str(x).lower()
            else:
                return x

        params = [
            (p[0], convert_bool(p[1])) for p in (
                ('tier', tier),
                ('model', model),
                ('version', version),
                ('language', language),
                ('detect_language', detect_language),
                ('punctuate', punctuate),
                ('profanity_filter', profanity_filter),
                ('redact', redact),
                ('diarize', diarize),
                ('diarize_version', diarize_version),
                ('ner', ner),
                ('multichannel', multichannel),
                ('alternatives', alternatives),
                ('numerals', numerals),
                ('paragraphs', paragraphs),
                ('summarize', summarize),
                ('detect_topics', detect_topics),
                ('utterances', utterances),
                ('utt_split', utt_split),
            ) if p[1] is not None
        ]
        if search is not None:
            for s in search:
                params.append(('search', s))
        if keywords is not None:
            for k in keywords:
                params.append(('keywords', k))
        if replace is not None:
            for k, v in replace.items():
                k = k.replace(':', '%3a')
                v = v.replace(':', '%3a')
                params.append(('replace', f'{k}:{v}'))

        headers = {
            'authorization': f'token {key}',
        }
        url = 'https://api.deepgram.com/v1/listen?{}'.format(urlencode(params))
        data = audio_data.get_wav_data()

        request = Request(url, data, headers)
        try:
            response = urlopen(request, timeout=self.operation_timeout)
        except HTTPError as e:
            raise sr.RequestError("recognition request failed: {}".format(e.reason))
        except URLError as e:
            raise sr.RequestError("recognition connection failed: {}".format(e.reason))

        result = json.load(response)

        if show_all:
            return result

        return result['results']['channels'][0]['alternatives'][0]['transcript']


class DeepgramSTT(STT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = self.config.get("key")
        if not self.key:
            raise ValueError("Api key for deepgram not set in mycroft.conf")
        self.recognizer = Recognizer()

    def execute(self, audio, language=None):
        lang = language or self.lang
        l1, l2 = lang.split("-")
        lang = f"{l1.lower()}-{l2.upper()}"
        utt = self.recognizer.recognize_deepgram(audio, language=lang, key=self.key)
        return utt


DeepgramSTTConfig = {}
