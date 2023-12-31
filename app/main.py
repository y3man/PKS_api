from typing import Annotated
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

import jwt
from jwt.exceptions import InvalidTokenError

from pydantic import BaseModel
# from starlette.responses import RedirectResponse

import json
import requests

ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = "B9JUtEup1FAoj9jkr1PoF7FDv8XLszYYqNMKfahjeBpNw2t4ud0gtgEZ8BHarNqV"
ALGORITHM = "HS256"


class Token(BaseModel):
    access_token: str
    token_type: str


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(username: str, password: str):
    if username == "student" and password == "student":
        return "student"
    return None


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    if username != "student":
        raise credentials_exception
    return username


@app.get("/")
async def root():
    return {"sitemap":
                {"/token": "Login to get access token",
                 "/link": "Interesting link",
                 "/methods": "HTTP methods and response codes",
                 "/weather": "Weather forecast in Bratislava",
                 # "/currency": "Currency exchange rates (EUR, USD, GBP, CZK)",
                 "/vat": "VAT rates in EU",
                 "/vat/{country}": "VAT rate in specific country"}
            }


@app.get("/link")
async def rickroll():
    return {"message": "Interesting page", "url": "bit.ly/3F3QgyV"}
    # return RedirectResponse("https://www.youtube.com/watch?v=dQw4w9WgXcQ")


@app.get("/methods")
async def methods(token: Annotated[str, Depends(get_current_user)]):
    # with open("methods.json", "r") as f:
    response = {"HTTP methods":
        {
            "GET": "The GET method requests a representation of the specified resource. Requests "
                   "using GET should only retrieve data.",
            "POST": "The POST method is used to submit an entity to the specified resource, "
                    "often causing a change in state or side effects on the server.",
            "PUT": "The PUT method replaces all current representations of the target resource with "
                   "the request payload.",
            "DELETE": "The DELETE method deletes the specified resource.",
            "PATCH": "The PATCH method is used to apply partial modifications to a resource.",
            "HEAD": "The HEAD method asks for a response identical to that of a GET request, "
                    "but without the response body.",
            "OPTIONS": "The OPTIONS method is used to describe the communication options for the "
                       "target resource.",
            "CONNECT": "The CONNECT method establishes a tunnel to the server identified by the "
                       "target resource.",
            "TRACE": "The TRACE method performs a message loop-back test along the path to the target "
                     "resource."},
        "HTTP status codes":
            {"1xx Informational": "The request was received, continuing process",
             "2xx Success": "The request was successfully received, understood, and accepted",
             "3xx Redirection": "Further action needs to be taken in order to complete the request",
             "4xx Client Error": "The request contains bad syntax or cannot be fulfilled",
             "5xx Server Error": "The server failed to fulfill an apparently valid request"}
    }
    return response


@app.get("/weather")
async def current_weather(token: Annotated[str, Depends(get_current_user)]):
    request = requests.get(
        "https://api.open-meteo.com/v1/forecast?latitude=48.1486&longitude=17.1077&daily=weathercode,"
        "temperature_2m_max,temperature_2m_min,sunrise,sunset,"
        "precipitation_sum&timezone=Europe%2FBerlin&forecast_days=1")
    response = json.loads(request.text)
    return response["daily"]


# @app.get("/currency")
# async def currency_exchange(token: Annotated[str, Depends(get_current_user)]):
#     request = requests.get("https://api.exchangerate.host/latest?base=EUR&symbols=USD,GBP,CZK")
#     response = json.loads(request.text)
#     return response["rates"]


@app.get("/vat")
async def vat(token: Annotated[str, Depends(get_current_user)]):
    request = requests.get("https://euvatrates.com/rates.json")
    response = json.loads(request.text)
    return response["rates"]


@app.get("/vat/{country}")
async def vat_country(country: str, token: Annotated[str, Depends(get_current_user)]):
    request = requests.get("https://euvatrates.com/rates.json")
    try:
        response = json.loads(request.text)["rates"][country.upper()]
    except KeyError:
        raise HTTPException(status_code=404, detail="Country not found")
    return response
