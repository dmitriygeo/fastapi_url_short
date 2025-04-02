from locust import HttpUser, task, between
import random
import string
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class URLShortenerUser(HttpUser):
    wait_time = between(1, 3)

    def random_string(self, length):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def on_start(self):
        self.email = f"user_{self.random_string(8)}@example.com"
        self.password = "password123"

        try:
            register_data = {
                "email": self.email,
                "password": self.password
            }
            register_response = self.client.post(
                "/api/v1/users/",
                json=register_data
            )
            if register_response.status_code not in [200, 201]:
                logger.error(f"Ошибка регистрации: {register_response.status_code}")
                logger.error(f"Response: {register_response.text}")
                return

            self.token = register_response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            logger.info(f"Успешная регистрация пользователя: {self.email}")

        except Exception as e:
            logger.error(f"Ошибка регистрации: {str(e)}")
            if 'register_response' in locals():
                logger.error(f"Response: {register_response.text}")

    @task(10)
    def create_short_link(self):
        """Создание короткой ссылки"""
        if not hasattr(self, 'headers'):
            logger.warning("No headers")
            return

        try:
            original_url = f"https://example.com/path/{self.random_string(8)}"
            response = self.client.post(
                "/api/v1/links/shorten",
                json={"original_url": original_url},
                headers=self.headers
            )

            if response.status_code != 200:
                logger.error(f"Ошибка при создании ссылки: {response.status_code}")
                logger.error(f"Response: {response.text}")
            else:
                logger.info(f"Успешное создание ссылки: {original_url}")

        except Exception as e:
            logger.error(f"Ошибка при создании ссылки: {str(e)}")

    @task(30)
    def access_short_link(self):
        if not hasattr(self, 'headers'):
            logger.warning("No headers")
            return

        try:
            original_url = f"https://example.com/path/{self.random_string(8)}"
            custom_alias = self.random_string(6)

            create_response = self.client.post(
                "/api/v1/links/shorten",
                json={"original_url": original_url, "custom_alias": custom_alias},
                headers=self.headers
            )

            if create_response.status_code == 200:
                short_code = create_response.json()["short_code"]
                access_response = self.client.get(f"/api/v1/{short_code}")

                if access_response.status_code != 200:
                    logger.error(f"Ошибка: {access_response.status_code}")
                    logger.error(f"Response: {access_response.text}")
                else:
                    logger.info(f"Успешный доступ к ссылке: {short_code}")
            else:
                logger.error(f"Ошибка: {create_response.status_code}")
                logger.error(f"Response: {create_response.text}")

        except Exception as e:
            logger.error(f"Ошибка доступа к ссылке: {str(e)}")

    @task(5)
    def get_link_stats(self):
        if not hasattr(self, 'headers'):
            logger.warning("No headers")
            return

        try:
            # Сначала создаем ссылку
            original_url = f"https://example.com/path/{self.random_string(8)}"
            create_response = self.client.post(
                "/api/v1/links/shorten",
                json={"original_url": original_url},
                headers=self.headers
            )
            if create_response.status_code == 200:
                short_code = create_response.json()["short_code"]
                stats_response = self.client.get(
                    f"/api/v1/links/{short_code}/stats",
                    headers=self.headers
                )
                if stats_response.status_code != 200:
                    logger.error(f"Ошибка при получении статистики: {stats_response.status_code}")
                    logger.error(f"Response: {stats_response.text}")
                else:
                    logger.info(f"Успешное получение статистики: {short_code}")

        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {str(e)}")