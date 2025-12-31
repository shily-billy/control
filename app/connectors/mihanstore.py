from app.connectors.base import BaseConnector, ConnectorResult


class MihanstoreConnector(BaseConnector):
    name = "mihanstore"

    async def login_test(self) -> ConnectorResult:
        # TODO: implement with Playwright
        return ConnectorResult(ok=False, message="not implemented")
