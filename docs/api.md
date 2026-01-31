# GitHub API Usage Documentation

This document outlines all the GitHub API endpoints used by this project. All interactions with the GitHub API are centralized in the `backend/app/clients/github_client.py` file.

The base URL for all API requests is: `https://api.github.com`

---

## 1. Search Repositories

- **Purpose**: Used by the background worker to find repositories based on various criteria (e.g., trending projects).
- **Function**: `search_repositories`
- **HTTP Method**: `GET`
- **Endpoint**: `/search/repositories`
- **Full URL**: `https://api.github.com/search/repositories`
- **Query Parameters**:
  | Parameter | Type | Description | Example |
  |---|---|---|---|
  | `q` | string | The search query string. Can contain qualifiers like `language:` or `stars:`. | `stars:>1000 language:python` |
  | `sort` | string | The field to sort results by. Defaults to `stars`. | `forks` |
  | `order`| string | The sort order, either `asc` or `desc`. Defaults to `desc`. | `asc` |
  | `per_page` | integer | The number of items to return per page. Defaults to `10`. | `30` |
  | `page` | integer | The page number of the results. Defaults to `1`. | `2` |

---

## 2. Get Repository Details

- **Purpose**: To fetch detailed information for a single repository.
- **Function**: `get_repository`
- **HTTP Method**: `GET`
- **Endpoint**: `/repos/{owner}/{repo}`
- **Full URL**: `https://api.github.com/repos/{owner}/{repo}`
- **URL Parameters**:
  | Parameter | Type | Description |
  |---|---|---|
  | `owner` | string | The username of the repository owner. |
  | `repo` | string | The name of the repository. |

---

## 3. List Releases

- **Purpose**: To retrieve a list of all releases for a specific repository. The client handles pagination to get the complete list.
- **Function**: `list_releases`
- **HTTP Method**: `GET`
- **Endpoint**: `/repos/{owner}/{repo}/releases`
- **Full URL**: `https://api.github.com/repos/{owner}/{repo}/releases`
- **URL Parameters**:
  | Parameter | Type | Description |
  |---|---|---|
  | `owner` | string | The username of the repository owner. |
  | `repo` | string | The name of the repository. |
- **Internal Query Parameters**:
  - `per_page`: Set to `100` to fetch a large number of releases per request.
  - `page`: Used internally to iterate through all pages of results.

---

## 4. Get Latest Release

- **Purpose**: To quickly fetch the single most recent release for a repository.
- **Function**: `get_latest_release`
- **HTTP Method**: `GET`
- **Endpoint**: `/repos/{owner}/{repo}/releases/latest`
- **Full URL**: `https://api.github.com/repos/{owner}/{repo}/releases/latest`
- **URL Parameters**:
  | Parameter | Type | Description |
  |---|---|---|
  | `owner` | string | The username of the repository owner. |
  | `repo` | string | The name of the repository. |

---

## 5. Get README

- **Purpose**: To fetch the rendered HTML content of a repository's README file.
- **Function**: `get_readme`
- **HTTP Method**: `GET`
- **Endpoint**: `/repos/{owner}/{repo}/readme`
- **Full URL**: `https://api.github.com/repos/{owner}/{repo}/readme`
- **URL Parameters**:
  | Parameter | Type | Description |
  |---|---|---|
  | `owner` | string | The username of the repository owner. |
  | `repo` | string | The name of the repository. |

---

## 6. Get Rate Limit Status

- **Purpose**: Used internally to monitor API usage and proactively avoid hitting rate limits.
- **Function**: `get_rate_limit`
- **HTTP Method**: `GET`
- **Endpoint**: `/rate_limit`
- **Full URL**: `https://api.github.com/rate_limit`
- **Parameters**: None

---

## 7. Get Authenticated User

- **Purpose**: To verify the provided GitHub token is valid and to get information about the user associated with the token.
- **Function**: `get_authenticated_user`
- **HTTP Method**: `GET`
- **Endpoint**: `/user`
- **Full URL**: `https://api.github.com/user`
- **Parameters**: None. Requires an `Authorization` header with a valid token.
