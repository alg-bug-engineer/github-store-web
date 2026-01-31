import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any, List
import redis
import time
import logging
import math
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qsl

from app.core.config import settings

logger = logging.getLogger(__name__)

class GitHubAPIClient:
    def __init__(self, token: Optional[str] = None):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token and token not in ("your_github_token", "", "ghp_xxxxx"):
            self.headers["Authorization"] = f"Bearer {token}"
        
        self.session = self._create_session()
        self.redis = None
        self.rate_limit_reset_time = 0
        self.rate_limit_remaining = -1
        self.request_delay_seconds = 1 # Be a bit faster with retries in place

    def _create_session(self) -> requests.Session:
        """Creates a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            # In Python 3.10+ you can use `respect_retry_after_header=True`
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _get_redis(self):
        if self.redis is None:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
                encoding="utf-8",
            )
        return self.redis

    def _check_rate_limit(self):
        redis_client = self._get_redis()
        rate_limit_info = redis_client.get("github_rate_limit")
        if rate_limit_info:
            try:
                info = json.loads(rate_limit_info)
                self.rate_limit_remaining = info.get("remaining", -1)
                self.rate_limit_reset_time = info.get("reset", 0)
            except json.JSONDecodeError:
                logger.warning("Failed to decode GitHub rate limit info from Redis.")
                self.rate_limit_remaining = -1

        if self.rate_limit_remaining < 50:
            logger.info("Fetching current GitHub API rate limit status.")
            try:
                limit_status = self._make_request_no_rate_check("GET", "/rate_limit")
                core_limit = limit_status.get("resources", {}).get("core", {})
                self.rate_limit_remaining = core_limit.get("remaining", 0)
                self.rate_limit_reset_time = core_limit.get("reset", time.time() + 3600)
                
                expiry_seconds = max(0, int(self.rate_limit_reset_time - time.time()) + 60)
                redis_client.set("github_rate_limit", json.dumps({
                    "remaining": self.rate_limit_remaining,
                    "reset": self.rate_limit_reset_time
                }), ex=expiry_seconds)
                logger.info(f"GitHub API Rate Limit: {self.rate_limit_remaining} remaining, resets at {datetime.fromtimestamp(self.rate_limit_reset_time)}")
            except Exception as e:
                logger.error(f"Failed to fetch GitHub rate limit: {e}")
                self.rate_limit_remaining = 0
                self.rate_limit_reset_time = time.time() + 3600

        if self.rate_limit_remaining <= 5:
            sleep_time = max(0, self.rate_limit_reset_time - time.time()) + 5
            if sleep_time > 0:
                logger.warning(f"GitHub API rate limit almost exhausted. Sleeping for {math.ceil(sleep_time / 60)} minutes.")
                time.sleep(sleep_time)
                self.rate_limit_remaining = -1
        
        time.sleep(self.request_delay_seconds)

    def _make_request_no_rate_check(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Internal method to make a request WITHOUT rate limit checking, using the session."""
        response = self.session.request(
            method=method,
            url=f"{self.base_url}{endpoint}",
            headers=self.headers,
            timeout=30,
            **kwargs,
        )
        response.raise_for_status()
        return response.json()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        self._check_rate_limit()
        try:
            response = self.session.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                headers=self.headers,
                timeout=30,
                **kwargs,
            )
            
            if "x-ratelimit-remaining" in response.headers:
                self.rate_limit_remaining = int(response.headers["x-ratelimit-remaining"])
                self.rate_limit_reset_time = int(response.headers["x-ratelimit-reset"])
                redis_client = self._get_redis()
                expiry_seconds = max(0, int(self.rate_limit_reset_time - time.time()) + 60)
                redis_client.set("github_rate_limit", json.dumps({
                    "remaining": self.rate_limit_remaining,
                    "reset": self.rate_limit_reset_time
                }), ex=expiry_seconds)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403 and "rate limit exceeded" in e.response.text.lower():
                logger.error(f"GitHub API rate limit exceeded (403). Pausing for 30 minutes.")
                time.sleep(30 * 60)
                self.rate_limit_remaining = -1
            raise

    def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 10,
        page: int = 1,
    ) -> Dict[str, Any]:
        params = {"q": query, "sort": sort, "order": order, "per_page": per_page, "page": page}
        return self._make_request("GET", "/search/repositories", params=params)

    def get_latest_release(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/repos/{owner}/{repo}/releases/latest")

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/repos/{owner}/{repo}")

    def get_readme(self, owner: str, repo: str) -> Dict[str, Any]:
        return self._make_request("GET", f"/repos/{owner}/{repo}/readme")

    def get_rate_limit(self) -> Dict[str, Any]:
        return self._make_request("GET", "/rate_limit")

    def get_authenticated_user(self) -> Dict[str, Any]:
        return self._make_request("GET", "/user")

    def list_releases(
        self, owner: str, repo: str
    ) -> List[Dict[str, Any]]:
        """List all releases for a repository, handling pagination."""
        all_releases = []
        url = f"/repos/{owner}/{repo}/releases"
        page = 1
        per_page = 100

        while True:
            params = {"per_page": per_page, "page": page}
            try:
                response = self.session.request(
                    method="GET",
                    url=f"{self.base_url}{url}",
                    headers=self.headers,
                    timeout=30,
                    params=params
                )
                
                if "x-ratelimit-remaining" in response.headers:
                    self.rate_limit_remaining = int(response.headers["x-ratelimit-remaining"])
                    self.rate_limit_reset_time = int(response.headers["x-ratelimit-reset"])
                    redis_client = self._get_redis()
                    expiry_seconds = max(0, int(self.rate_limit_reset_time - time.time()) + 60)
                    redis_client.set("github_rate_limit", json.dumps({
                        "remaining": self.rate_limit_remaining,
                        "reset": self.rate_limit_reset_time
                    }), ex=expiry_seconds)

                response.raise_for_status()
                releases_page = response.json()
                if not releases_page:
                    break

                all_releases.extend(releases_page)

                if 'link' in response.headers:
                    links = requests.utils.parse_header_links(response.headers['link'])
                    next_link = next((link for link in links if link.get('rel') == 'next'), None)
                    if next_link:
                        next_url_parts = urlparse(next_link['url'])
                        query_params = dict(parse_qsl(next_url_parts.query))
                        page = int(query_params.get('page', page))
                    else:
                        break
                else:
                    break
                
                time.sleep(self.request_delay_seconds)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403 and "rate limit exceeded" in e.response.text.lower():
                    logger.error("GitHub API rate limit exceeded during pagination. Pausing for 30 minutes.")
                    time.sleep(30 * 60)
                    self.rate_limit_remaining = -1
                else:
                    logger.error(f"Error fetching releases for {owner}/{repo}: {e}")
                    break 
            except requests.exceptions.RequestException as e:
                logger.error(f"A network error occurred while fetching releases for {owner}/{repo}: {e}")
                break

        return all_releases

github_client = GitHubAPIClient(token=settings.GITHUB_TOKEN)
