from fastapi import APIRouter, File, UploadFile
from mfcc import calculate_mfcc, read_from_path
import time
import sys
sys.path.append('.')


router = APIRouter(prefix='/api', tags=["api"])


@router.post('/mfcc')
async def mfcc_api(audio_file: UploadFile = File(...), frame_ms: float = 25, hop_ms: float = 10, n_mels: int = 128, num_ceps: int = 13):
    start = time.time()
    audio_vec, sr = read_from_path(audio_file.file, mode="api")
    mfcc_features = calculate_mfcc(
        audio_vec, sr, frame_ms, hop_ms, n_mels, num_ceps)

    end = time.time()
    return {'mfcc_features': mfcc_features.tolist(), 'total_time': end-start}
