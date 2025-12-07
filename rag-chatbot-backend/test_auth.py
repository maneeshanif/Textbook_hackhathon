"""Quick test script for auth endpoints"""
import asyncio
import httpx

API_URL = "http://localhost:8000"

async def test_signup():
    async with httpx.AsyncClient() as client:
        print("🧪 Testing signup...")
        response = await client.post(
            f"{API_URL}/api/auth/signup",
            json={
                "email": "testuser@example.com",
                "password": "TestPass123",
                "fullName": "Test User"
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json() if response.status_code == 201 else None

async def test_login(email, password):
    async with httpx.AsyncClient() as client:
        print("\n🧪 Testing login...")
        response = await client.post(
            f"{API_URL}/api/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

async def main():
    signup_result = await test_signup()
    if signup_result:
        await test_login("testuser@example.com", "TestPass123")

if __name__ == "__main__":
    asyncio.run(main())
