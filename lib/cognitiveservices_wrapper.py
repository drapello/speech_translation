#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root for full license information.

import time
from conf import config 
import azure.cognitiveservices.speech as speechsdk

# Set up the subscription info for the Speech Service:
# Replace with your own subscription key and service region (e.g., "westus").

def translation_once_from_mic():
    """performs one-shot speech translation from input from an audio file"""
    # <TranslationOnceWithMic>
    # set up translation parameters: source language and target languages
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=config.SPEECH_KEY, region=config.SERVICE_REGION,
        speech_recognition_language=config.SPEECH_RECOGNITION_LANGUAGE,
        target_languages=config.LANGUAGES)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    # Creates a translation recognizer using and audio file as input.
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config, audio_config=audio_config)

    # Starts translation, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognized text as well as the translation.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
    result = recognizer.recognize_once()
    return result.json

def translation_continuous():
    """performs continuous speech translation from input from an audio file"""
    # <TranslationContinuous>
    # set up translation parameters: source language and target languages
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription=config.SPEECH_KEY, region=config.SERVICE_REGION,
        speech_recognition_language='en-US',
        target_languages=config.LANGUAGES, voice_name="de-DE-Hedda")

    # weatherfilename = "whatstheweatherlike.wav"
    # audio_config = speechsdk.audio.AudioConfig(filename=weatherfilename)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)


    # Creates a translation recognizer using and audio file as input.
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config, audio_config=audio_config)

    def result_callback(event_type, evt):
        """callback to display a translation result"""
        print("{}: {}\n\tTranslations: {}\n\tResult Json: {}".format(
            event_type, evt, evt.result.translations.items(), evt.result.json))

    done = False

    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    # connect callback functions to the events fired by the recognizer
    recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    # event for intermediate results
    recognizer.recognizing.connect(lambda evt: result_callback('RECOGNIZING', evt))
    # event for final result
    recognizer.recognized.connect(lambda evt: result_callback('RECOGNIZED', evt))
    # cancellation event
    recognizer.canceled.connect(lambda evt: print('CANCELED: {} ({})'.format(evt, evt.reason)))

    # stop continuous recognition on either session stopped or canceled events
    recognizer.session_stopped.connect(stop_cb)
    recognizer.canceled.connect(stop_cb)

    def synthesis_callback(evt):
        """
        callback for the synthesis event
        """
        print('SYNTHESIZING {}\n\treceived {} bytes of audio. Reason: {}'.format(
            evt, len(evt.result.audio), evt.result.reason))

    # connect callback to the synthesis event
    recognizer.synthesizing.connect(synthesis_callback)

    # start translation
    recognizer.start_continuous_recognition()

    while not done:
        time.sleep(.5)
    # </TranslationContinuous>

