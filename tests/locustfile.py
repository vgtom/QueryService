from locust import HttpUser, task, between

class QueryManagerUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Get authentication token
        response = self.client.post("/api/v1/token", data={
            "username": "test_user",
            "password": "test_password"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task
    def store_query(self):
        self.client.post(
            "/api/v1/queries/",
            json={
                "user_id": "test_user",
                "query_text": "SELECT * FROM users"
            },
            headers=self.headers
        )
    
    @task
    def get_queries(self):
        self.client.get(
            "/api/v1/queries/?user_id=test_user",
            headers=self.headers
        )
    
    @task
    def analyze_query(self):
        self.client.post(
            "/api/v1/queries/analyze",
            json={"query_text": "SELECT * FROM users"},
            headers=self.headers
        ) 