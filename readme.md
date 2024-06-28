## Description

A stt plugin for ovos using [Deepgram](https://deepgram.com/)

## Install

`pip install ovos-stt-plugin-deepgram`


## Configuration

By default the global language used by mycroft-core will be used

```json
    "stt": {
        "module": "ovos-stt-plugin-deepgram",
        "ovos-stt-plugin-deepgram": {
            "key": "your_api_key",
            "model": "nova-2-conversationalai"  // Can be one of: 'nova-2-general', 'nova-2-meeting', 'nova-2-phonecall', 'nova-2-voicemail', 'nova-2-finance', 'nova-2-conversationalai', 'nova-2-video', 'nova-2-medical', 'nova-2-drivethru', 'nova-2-automotive'
        }
    }
```

Note: Model `conversationalai` is EN-US / EN only!
More info on models: https://developers.deepgram.com/docs/model
