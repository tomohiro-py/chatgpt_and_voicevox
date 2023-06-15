import pyaudio
import wave
import io
from time import sleep
import queue

def play_wav(wav_file_path: str):
        wr: wave.Wave_read = wave.open(wav_file_path, 'r')
        p = pyaudio.PyAudio()
        stream = p.open(
            format=p.get_format_from_width(wr.getsampwidth()),
            channels=wr.getnchannels(),
            rate=wr.getframerate(),
            output=True
        )
        chunk = 1024
        data = wr.readframes(chunk)
        while data:
            stream.write(data)
            data = wr.readframes(chunk)
        sleep(.5)
        stream.close()
        p.terminate()

def play_wave(wave_binary: bytes):

    # メモリ上で展開
    audio = io.BytesIO(wave_binary)

    with wave.open(audio,'rb') as f:
        # 以下再生用処理
        p = pyaudio.PyAudio()

        def _callback(in_data, frame_count, time_info, status):
            data = f.readframes(frame_count)
            return (data, pyaudio.paContinue)

        stream = p.open(format=p.get_format_from_width(width=f.getsampwidth()),
                        channels=f.getnchannels(),
                        rate=f.getframerate(),
                        output=True,
                        stream_callback=_callback)

        # Voice再生
        stream.start_stream()
        while stream.is_active():
            sleep(0.1)

        stream.stop_stream()
        stream.close()
        p.terminate()


def play_wav_with_queue(multi_process_queue)->None:

    p = pyaudio.PyAudio()
    chunk = 1024

    while True:
        try:
            wave_binary = multi_process_queue.get(timeout=15)

            if wave_binary == '[DONE]':
                break
            else:
                wr = wave.open(io.BytesIO(wave_binary))
                stream = p.open(
                    format=p.get_format_from_width(wr.getsampwidth()),
                    channels=wr.getnchannels(),
                    rate=wr.getframerate(),
                    output=True
                )
                data = wr.readframes(chunk)

                while data:
                    stream.write(data)
                    data = wr.readframes(chunk)
                else:
                    stream.close()
                    sleep(.3)

        except queue.Empty:
            break
        except KeyboardInterrupt as e:
            print("KeyboardInterrupt was detected.")
            break
        except Exception:
            break

    p.terminate()

def wave_to_wav_file(path, wave_format_binary) -> None:
    with open(path, 'wb') as f:
        f.write(wave_format_binary)