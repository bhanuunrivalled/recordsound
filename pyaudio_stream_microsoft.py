import azure.cognitiveservices.speech as speechsdk
import pyaudio

speech_key, service_region = "", "westus"
finalResultSRC = ""
finalResultDst = ""

RATE = 48000
KHz_RATE = int(RATE/1000)
CHUNK = int(RATE)


def translation_continuous():
    """performs continuous speech translation from input from an audio file"""
    # <TranslationContinuous>
    # set up translation parameters: source language and target languages
    translation_config = speechsdk.translation.SpeechTranslationConfig(
        subscription='<your subscription key>', region='northeurope',
        speech_recognition_language='de-DE',
        target_languages=('en-US', 'fr'))

    # setup the audio stream
    audioFormat = speechsdk.audio.AudioStreamFormat(
        samples_per_second=RATE, bits_per_sample=16, channels=2)
    stream = speechsdk.audio.PushAudioInputStream(audioFormat)

    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    # Creates a translation recognizer using and audio file as input.
    recognizer = speechsdk.translation.TranslationRecognizer(
        translation_config=translation_config, audio_config=audio_config)

    def result_callback(event_type, evt):
        """callback to display a translation result"""
        # print("{}: {}\n\tTranslations: {}\n\tResult Json: {}".format(
        # event_type, evt, evt.result.translations.items(), evt.result.json))
        print(evt)
        if event_type == "RECOGNIZING":
            # Translate
            print(evt.result.translations.items()[0][1])
            # Original
            # print(type(evt.result.json))

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    # connect callback functions to the events fired by the recognizer
    recognizer.session_started.connect(
        lambda evt: print('SESSION STARTED: {}'.format(evt)))
    recognizer.session_stopped.connect(
        lambda evt: print('SESSION STOPPED {}'.format(evt)))
    # event for intermediate results
    recognizer.recognizing.connect(
        lambda evt: result_callback('RECOGNIZING', evt))
    # event for final result
    recognizer.recognized.connect(
        lambda evt: result_callback('RECOGNIZED', evt))
    # cancellation event
    recognizer.canceled.connect(lambda evt: print(
        'CANCELED: {} ({})'.format(evt, evt.reason)))

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
    # start pushing data until all data has been read from the file
    # 6 from headphone and 4 from speaker
    try:
        p = pyaudio.PyAudio()
        pstream = p.open(
            format=pyaudio.paInt16,
            channels=2, rate=RATE,
            input=True, frames_per_buffer=CHUNK,
            input_device_index=6,
            as_loopback=True
        )
        while(True):
            frame = pstream.read(CHUNK)

            #frames = wav_fh.readframes(n_bytes)
            #print('read {} bytes'.format(len(frames)))
            # if not frames:
            #     print('break')
            #     break
            if frame:
                #ch1 = cutChannelFromStream(frame, 1, 2)
                #print('got frame from speakers')
                stream.write(frame)
            #time.sleep(1)

    finally:
        # stop recognition and clean up
        stream.close()
        recognizer.stop_continuous_recognition()

    print(finalResultSRC)
    # recognizer.stop_continuous_recognition()
    # </TranslationContinuous>


translation_continuous()