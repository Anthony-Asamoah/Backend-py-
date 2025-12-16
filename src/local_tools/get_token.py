import datetime
import logging
import sys
from typing import Optional

import httpx
import pyperclip
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

url = 'http://127.0.0.1:80/api/v1/user-account/login'

default_identifier = '0503032976'
default_password = 'openforme'


class CmdOptions(BaseModel):
    path: Optional[str] = __name__
    identifier: Optional[str] = default_identifier
    password: Optional[str] = default_password


class Creds(BaseModel):
    identifier: str
    password: str


class User(BaseModel):
    title: str
    last_name: str
    first_name: str
    other_names: Optional[str]
    date_of_birth: datetime.date
    gender: str
    nationality: str
    email: str
    phone_number: str
    id: str
    age: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_info: Optional[User] = None


def get_cmd_params(args: Optional[list]) -> CmdOptions:
    if not args: return CmdOptions()
    match len(args):
        case 1:
            return CmdOptions(path=args[0])
        case 2:
            return CmdOptions(
                path=args[0],
                identifier=args[1],
            )
        case 3:
            return CmdOptions(
                path=args[0],
                identifier=args[1],
                password=args[2],
            )
        case _:
            raise Exception(
                'invalid number of arguments. '
                'expected format: [interpreter] [path] [<optional>identifier] [<optional>password]. '
                'example: python emi_login.py 0503032976 password'
            )


def main(cmd_args: CmdOptions = CmdOptions()):
    creds = Creds(
        identifier=cmd_args.identifier,
        password=cmd_args.password
    )
    response = httpx.post(
        url=url,
        json=creds.__dict__,
        timeout=10
    )
    try:
        response.raise_for_status()
        result = LoginResponse(**response.json())
    except httpx.HTTPError as e:
        print(e.response.text)
    except:
        logging.exception('something went wrong')
        print(response.text)
    else:
        print('token:', result.access_token)
        pyperclip.copy(result.access_token)
        return result


if __name__ == '__main__':
    """
    run command: [interpreter] [path] [identifier] [password]
    """
    cmd_args = get_cmd_params(sys.argv)
    main(cmd_args)
