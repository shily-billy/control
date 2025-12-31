from dataclasses import dataclass


@dataclass
class ConnectorResult:
    ok: bool
    message: str


class BaseConnector:
    name: str

    async def login_test(self) -> ConnectorResult:
        raise NotImplementedError
