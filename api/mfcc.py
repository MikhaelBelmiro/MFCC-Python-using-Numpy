import io
import ffmpeg

import numpy as np

from wave import Wave_read


def buffer_to_array(buf):
    max_int = np.iinfo(np.int16).max + 1
    arr = np.frombuffer(buf, dtype='<u2').astype(np.int16)/max_int
    arr = arr.reshape(1, -1)
    return arr


def read_from_path(path, mode="local"):
    if mode == "local":
        with open(path, "rb") as audio_buffer:
            audio_buffer = audio_buffer.read()
    elif mode == "api":
        path.seek(0)
        audio_buffer = path.read()
    audio_buffer, _ = (
        ffmpeg
        .input("-")
        .output("-", format="wav", ac=1, ar=16_000, bits_per_raw_sample=16)
        .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=audio_buffer)
    )
    audio_buffer = Wave_read(io.BytesIO(audio_buffer))
    audio_buffer = audio_buffer.readframes(audio_buffer.getnframes())

    return buffer_to_array(audio_buffer), 16_000


def create_hamming_window(frame_length):
    arr = np.cos((np.arange(frame_length)*2*np.math.pi)/(frame_length-1))
    hamming = 0.54 - 0.46*arr
    return hamming


def create_fft_matrix(length):
    square_matrix = np.arange(length).reshape(
        (-1, 1))*np.arange(length).reshape((1, -1))
    power_constant = (-1j*2*np.math.pi)/length
    dft_matrix = np.exp(power_constant*square_matrix)
    return dft_matrix


def mel_to_hz(mel):
    return 700*(10**(mel/2595) - 1)


def hz_to_mel(hz):
    return 2595*np.log10(1+(hz/700))


def create_mel_matrix(bank_size, n_fft, sr, low_hz=0, high_hz=None):
    if high_hz is None:
        high_hz = sr/2
    low_mel = hz_to_mel(low_hz)
    high_mel = hz_to_mel(high_hz)
    mel_points = np.linspace(low_mel, high_mel, bank_size + 2)
    hz_points = mel_to_hz(mel_points)

    bins = np.floor((n_fft + 1) * hz_points / sr)

    mat = np.zeros((bank_size, n_fft//2 + 1))
    for filter_index in range(1, bank_size+1):
        low_filter_bin, center_filter_bin, high_filter_bin = int(
            bins[filter_index - 1]), int(bins[filter_index]), int(bins[filter_index + 1])
        mat[filter_index-1, low_filter_bin:center_filter_bin] = (np.arange(
            low_filter_bin, center_filter_bin) - low_filter_bin)/(center_filter_bin - low_filter_bin)
        mat[filter_index-1, center_filter_bin:high_filter_bin] = (high_filter_bin - np.arange(
            center_filter_bin, high_filter_bin))/(high_filter_bin - center_filter_bin)
    return mat


def create_dct_matrix(length):
    ns = np.arange(length)
    ks = np.arange(length) + (1/2)
    mat = np.cos((ns.reshape((-1, 1))@ks.reshape((1, -1)))*(np.math.pi/length))
    mat[:, 0] = 1/2
    return mat


def calculate_mfcc(audio_vec, sr, frame_ms=25.0, hop_ms=10.0, n_mels=128, num_ceps=13):
    audio_vec = audio_vec.reshape(
        1, -1) if len(audio_vec.shape) == 2 else audio_vec
    frame_num = audio_vec.shape[1]

    frame_length = int((frame_ms/1000)*sr)
    num_pad = ((frame_num//frame_length)+1)*frame_length - \
        frame_num if frame_num % frame_length != 0 else 0
    audio_vec = np.pad(audio_vec, ((0, 0), (0, num_pad)))
    hop_length = int((hop_ms/1000)*sr)

    mfcc_output = np.empty((0, num_ceps))
    min_float = np.finfo(np.float64).eps
    hamming_window = create_hamming_window(frame_length)
    dft_matrix = create_fft_matrix(frame_length)
    mel_matrix = create_mel_matrix(n_mels, frame_length, sr)
    dct_matrix = create_dct_matrix(n_mels)

    for i in range(0, frame_num, hop_length):
        chunk_vec = audio_vec[:, i: i+frame_length]
        chunk_vec = hamming_window*chunk_vec
        chunk_vec = (dft_matrix@chunk_vec.T).reshape((1, -1))

        if chunk_vec.shape[1] % 2 == 0:
            chunk_vec = chunk_vec[:, :frame_length//2+1]
        else:
            chunk_vec = chunk_vec[:, :(frame_length+1)//2]

        chunk_vec = (np.absolute(chunk_vec)**2)/frame_length
        filter_banks = np.dot(chunk_vec, mel_matrix.T)
        filter_banks = np.where(np.absolute(
            filter_banks) <= min_float, min_float, filter_banks)
        filter_banks = np.log10(filter_banks)
        filter_banks = (dct_matrix@filter_banks.reshape((-1, 1))
                        ).reshape((1, -1))[:, :num_ceps]
        filter_banks -= filter_banks.mean(axis=1)
        mfcc_output = np.concatenate((mfcc_output, filter_banks), axis=0)
    return mfcc_output.T
