import os
import uvicorn
import routers
import argparse

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

parser = argparse.ArgumentParser()
parser.add_argument("--reload", action='store_true',
                    default=False, help="Run uvicorn with reload")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(routers.router)

if '.env' in os.listdir():
    load_dotenv('.env')

HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '7071'))


@app.get('/')
async def root():
    return {'message': 'This is an MFCC App'}


if __name__ == '__main__':
    args = parser.parse_args()
    uvicorn.run('main:app', reload=args.reload, host=HOST, port=PORT)
