import httpx
import pytest
from kall.providers.greenhouse import GreenhouseProvider


@pytest.mark.asyncio
async def test_greenhouse_normalizes_jobs():
    def handler(request):
        return httpx.Response(200,json={"jobs":[{"id":1,"title":"Director of Engineering","absolute_url":"https://x/job/1","content":"Lead teams","location":{"name":"Remote"}}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        jobs=await GreenhouseProvider(client).collect("Acme","acme")
    assert jobs[0].company=="Acme"
    assert jobs[0].title=="Director of Engineering"
