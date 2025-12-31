from app.connectors.base import BaseConnector, ConnectorResult


class MemarketConnector(BaseConnector):
    name = "memarket"

    async def login_test(self) -> ConnectorResult:
        # TODO: implement with Playwright (Nuxt SPA)
        return ConnectorResult(ok=False, message="not implemented")
