import pvporcupine
from pvrecorder import PvRecorder

from main_loop import main_loop
from my_module import play_wavfile

picovoice_api_key = '+HnEVjviQ1C2gGEnMlCUPHiYPo5eug62cpp/Ofdvv4WSYstgLdro2Q=='

def wake_word_loop():
    keyword_paths = ['picovoice_model/ぼーるっこ_ja_windows_v2_2_0.ppn', 'picovoice_model/ひなあられ_ja_windows_v2_2_0.ppn']
    model_path = 'picovoice_model/porcupine_params_ja.pv'
    device_index = -1
    sensitivities = [0.5] * len(keyword_paths)

    try:
        porcupine = pvporcupine.create(
            access_key=picovoice_api_key,
            # keywords=keywords
            keyword_paths=keyword_paths,
            model_path=model_path,
            sensitivities=sensitivities,
            )
    except Exception as e:
        print(e)

    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=device_index)
    recorder.start()
    print('Listening ... (press Ctrl+C to exit)')

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if result >= 0:
                recorder.stop()
                play_wavfile('wave_file/wake_up.wav')
                main_loop()
                recorder.start()

    except KeyboardInterrupt:
        print('Stopping ...')
    finally:
        recorder.delete()
        porcupine.delete()

if __name__ == '__main__':
    wake_word_loop()