import asyncio

async def test_simple_async_function():
    await asyncio.sleep(0.1)
    assert True
