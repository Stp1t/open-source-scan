import requests
import json
from datetime import datetime, timezone
import time
from score_algo import get_final_score_dict, contributor_score, average_pr_wait_time_score, popularity_score
import weights

API_KEY = ""

#-----------HELPER FUNCTIONS----------------

def get_release_amount(releases_url, headers):
    # fetches the amount of releases in a github repo

    release_count = 0
    page = 1

    while True:
        response = requests.get(releases_url, headers=headers, params={"page": page, "per_page": 100})
        releases = response.json()

        if not releases:
            break

        release_count += len(releases)
        page += 1

    return release_count

def get_age_of_repo_in_years_and_descp_and_pic(repo_info_url, headers):
    response = requests.get(repo_info_url, headers=headers)
    repo_info = response.json()

    created_at = repo_info["created_at"]
    description = repo_info["description"]
    picture_url = repo_info["owner"]["avatar_url"]

    creation_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    current_date = datetime.now()
    age_in_days = (current_date - creation_date).days
    age_in_years = age_in_days / 365.25
    return age_in_years, description, picture_url

def calculate_average_releases_per_year(age_in_years, release_amount):
    return release_amount/age_in_years

def calculate_average_commits_per_year(age_in_years, commit_amount):
    return commit_amount/age_in_years

def get_contributor_amount(contributors_url, headers):
    # fetches the amount of contributors in a github repo

    contributor_count = 0
    page = 1

    while True:
        response = requests.get(contributors_url, headers=headers, params={"page": page, "per_page": 100})
        contributors = response.json()

        if not contributors:
            break

        contributor_count += len(contributors)
        page += 1

    return contributor_count


def get_days_since_last_commit(commits_url, headers):
    # fetches the days since last commit in a github repo

    response = requests.get(commits_url, headers=headers, params={"per_page": 1, "page": 1})
    commits = response.json()

    if response.status_code != 200 or not commits:
        return None

    if isinstance(commits, list) and commits:
        last_commit = commits[0]
        last_commit_date = last_commit['commit']['committer']['date']
        return days_since_date(last_commit_date)
    else:
        return None

def get_days_since_last_release(releases_url, headers):
    # fetches the days since last release in a github repo

    response = requests.get(releases_url, headers=headers, params={"per_page": 1, "page": 1})
    releases = response.json()

    if response.status_code != 200 or not releases:
        return None

    if isinstance(releases, list) and releases:
        last_release = releases[0]
        last_release_date = last_release['published_at']
        return days_since_date(last_release_date)
    else:
        return None


def days_since_date(date_string):
    # calculates days passed from specific date to today

    if not date_string:
        return None

    date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    date = date.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    delta = now - date
    return delta.days


def get_repo_activity(activity_url, headers):
    # fetch activity characteristics like open issues, forks, stars
        response = requests.get(activity_url, headers=headers)

        if response.status_code == 200:
            repo_data = response.json()
            return repo_data["open_issues_count"], repo_data["forks_count"], repo_data["watchers_count"], repo_data["stargazers_count"]
        else:
            print(f"Error: {response.status_code}, {response.json().get('message', 'An error occurred')}")
            return None


def check_dependabot(dependabot_url, headers, print_info=False):
    # checks if dependabot exists

    response = requests.get(dependabot_url, headers=headers)

    if response.status_code == 204:
        if print_info: print("Dependabot vulnerability alerts are enabled for this repository (no active alerts yet).")
        return True
    elif response.status_code == 200:
        if print_info: print("Dependabot vulnerability alerts are enabled and there are active alerts for this repository.")
        return True
    elif response.status_code == 404:
        if print_info:print("Dependabot vulnerability alerts are not enabled for this repository.")
        return False
    elif response.status_code == 401 :
        if print_info: print("Error: 401 Unauthorized - Check your GitHub token and permissions.")
        return None
    else:
        if print_info: print(f"Error: {response.status_code} - {response.json().get('message', '')}")
        return None


def check_security_md(security_url, headers, print_info=False):
    # checks if security_md exists

    response = requests.get(security_url, headers=headers)

    if response.status_code == 200:
        if print_info: print("SECURITY.md file found in the repository.")
        return True
    elif response.status_code == 404:
        if print_info: print("SECURITY.md file not found in the repository.")
        return False
    else:
        if print_info: print(f"Error: {response.status_code} - {response.json().get('message', '')}")
        return None


def get_commit_amount(commits_url, headers):
    # gets amount of commits

    while True:
        response = requests.get(commits_url, headers=headers)
        if response.status_code == 202:
            time.sleep(1)
            continue
        elif response.status_code == 200:
            break
        else:
            raise Exception(f'error while fetching commit data: {response.status_code}')

    data = response.json()
    total_commits = sum(contributor['total'] for contributor in data)
    return total_commits

def get_github_dependencies(owner, repo, headers):
    # get dependencies from github repo
        url = "https://api.github.com/graphql"

        # GraphQL query to retrieve dependencies
        query = """
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            dependencyGraphManifests(first: 100) {
              nodes {
                filename
                dependencies(first: 100) {
                  nodes {
                    packageName
                    requirements
                    hasDependencies
                  }
                }
              }
            }
          }
        }
        """

        # Setting variables for the query
        variables = {
            "owner": owner,
            "repo": repo
        }

        # Send the request
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers
        )

        # Check if request was successful
        if response.status_code != 200:
            raise Exception(f"Query failed with status code {response.status_code}: {response.text}")

        data = response.json()

        # Parse the response to extract dependencies
        dependencies = []

        manifest_dependencies_count = {}
        transitive_dependencies_count = 0
        direct_dependencies_count = 0

        manifests = data.get("data", {}).get("repository", {}).get("dependencyGraphManifests", {}).get("nodes", [])
        for manifest in manifests:
            filename = manifest["filename"]
            manifest_count = 0
            for dep in manifest["dependencies"]["nodes"]:
                dependencies.append({
                    "filename": filename,
                    "package_name": dep["packageName"],
                    "requirements": dep["requirements"],
                    "has_dependencies": dep["hasDependencies"]
                })
                manifest_count += 1
                if dep["hasDependencies"]:
                    transitive_dependencies_count += 1
                else:
                    direct_dependencies_count += 1
            manifest_dependencies_count[filename] = manifest_count

        total_dependencies = len(dependencies)
        return total_dependencies

def get_average_time_to_fix(issues_url, headers, max_pages=5, print_info=False):
    # get average time to fix an issue (in hours)

    page = 1
    time_deltas = []
    while True:
        response = requests.get(issues_url, headers=headers,
                                params={"state": "closed", "per_page": 100, "page": page, "label": "bug"})

        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.json().get('message', 'Unknown error')}")
            break

        issues = response.json()

        if not issues or page > max_pages:
            break

        for issue in issues:
            if 'created_at' in issue and 'closed_at' in issue and 'pull_request' not in issue:  # Only proceed if timestamps are present
                created_at = datetime.strptime(issue['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                closed_at = datetime.strptime(issue['closed_at'], "%Y-%m-%dT%H:%M:%SZ")

                time_diff = (closed_at - created_at).total_seconds() / 3600
                time_deltas.append(time_diff)

        page += 1

    average_time_to_fix = sum(time_deltas) / len(time_deltas) if time_deltas else 0

    if print_info: print(f"Average time to fix issues: {average_time_to_fix:.2f} hours")

    return round(average_time_to_fix/24, 2)


def get_average_time_to_merge(merge_url, headers, max_pages=5, print_info=False):
    # get average time to merge (in hours)

    page = 1
    time_deltas = []
    while True:
        response = requests.get(merge_url, headers=headers, params={"state": "closed", "per_page": 100, "page": page})

        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.json().get('message', 'Unknown error')}")
            break

        pull_requests = response.json()
        if not pull_requests or page > max_pages:
            break

        time_deltas.extend(
            (datetime.strptime(pr['merged_at'], "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(pr['created_at'],
                                                                                          "%Y-%m-%dT%H:%M:%SZ")).total_seconds() / 3600
            for pr in pull_requests
            if pr['merged_at'] is not None
        )

        page += 1

    average_time_to_merge = sum(time_deltas) / len(time_deltas) if time_deltas else 0
    if print_info: print(f"Average time from PR creation to merge: {average_time_to_merge:.2f} hours")
    return round(average_time_to_merge/24, 2)


#-----------MAIN FUNCTION----------------------------

def get_github_repo_info(repo_url):
    # base url
    api_base_url = "https://api.github.com"

    # get owner and repo name
    parts = repo_url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]

    repo_info_url = f"{api_base_url}/repos/{owner}/{repo}"
    commits_url = f'{api_base_url}/repos/{owner}/{repo}/stats/contributors'
    commits_date_url = f'{api_base_url}/repos/{owner}/{repo}/commits'
    releases_url = f"{api_base_url}/repos/{owner}/{repo}/releases"
    contributors_url = f"{api_base_url}/repos/{owner}/{repo}/contributors"
    activity_url = f'{api_base_url}/repos/{owner}/{repo}'
    dependabot_url = f"{api_base_url}/repos/{owner}/{repo}/vulnerability-alerts"
    security_url = f"{api_base_url}/repos/{owner}/{repo}/contents/SECURITY.md"
    issues_url = f"{api_base_url}/repos/{owner}/{repo}/issues"
    pull_url = f"{api_base_url}/repos/{owner}/{repo}/pulls"


    headers = {
        "Accept": "application/vnd.github+json",
        'Authorization': f'token {API_KEY}',
        "Content-Type": "application/json"
    }


    try:
        age_of_repo, description, picture_url = get_age_of_repo_in_years_and_descp_and_pic(repo_info_url, headers)
        commits = get_commit_amount(commits_url, headers)
        releases = get_release_amount(releases_url, headers)
        avg_releases_per_year = calculate_average_releases_per_year(age_of_repo, releases)
        avg_commits_per_year = calculate_average_commits_per_year(age_of_repo, commits)
        contributors = get_contributor_amount(contributors_url, headers)
        last_commit = get_days_since_last_commit(commits_date_url, headers)
        last_release = get_days_since_last_release(releases_url, headers)
        open_issues, forks_count, watchers_count, stargazers_count = get_repo_activity(activity_url,headers)
        is_dependabot = check_dependabot(dependabot_url, headers)
        is_security_md = check_security_md(security_url, headers)
        avg_time_for_issue = get_average_time_to_fix(issues_url, headers)
        avg_time_to_merge = get_average_time_to_merge(pull_url, headers)
        total_dependencies = get_github_dependencies(owner,repo,headers)

        final_dict = get_final_score_dict(contributors, avg_commits_per_year, forks_count, stargazers_count, last_commit, last_release, avg_time_for_issue, avg_time_to_merge, total_dependencies,is_dependabot,is_security_md,avg_releases_per_year)
        return json.dumps({
            "repo_name": repo,
            "owner": owner,
            "description":description,
            "picture_url": picture_url,
            "contributors": {
                "value": contributors,
                "score": final_dict["contributor_score"],
                "title": "Number of contributors",
                "description": "The number of unique contributors who have made changes to the repository reflects the size and engagement of the project's community. The score is calculated dependen on the size of the repository.",
                "weight": weights.CONTRIBUTOR_WEIGHT
            },
            "avg_commits_per_year": {
                "value": avg_commits_per_year,
                "score": final_dict["commit_score"],
                "title": "Average commits per year",
                "description": "The number of commits per year made to the repository is a strong indicator of an active and maintained project. A high number of commits suggests developers are regularly improving and updating the codebase, while a low number could mean the project is not actively developed.",
                "weight": weights.COMMIT_WEIGHT
            },
            "avg_releases_per_year": {
                "value": avg_releases_per_year,
                "score": final_dict["releases_score"],
                "title": "Average releases per year",
                "description": "Tracking the number of releases or versions made available per year provides insight into how actively the project is being developed. Frequent releases indicate the project is delivering new features and bug fixes to users, whereas infrequent releases may signal a lack of active maintenance.",
                "weight": weights.RELEASES_WEIGHT
            },
            "days_since_last_commit": {
                "value": last_commit,
                "score": final_dict["time_since_last_commit_score"],
                "title": "Days since last commit",
                "description": "The time elapsed since the last commit was made provides an indication of how actively the project is being developed. Recent commits demonstrate the project is actively maintained, whereas a long time since the last commit may signal the project is no longer a priority.",
                "weight": weights.TIME_SINCE_LAST_COMMIT_WEIGHT
            },
            "days_since_last_release": {
                "value": last_release,
                "score": final_dict["time_since_last_release_score"],
                "title": "Days since last release",
                "description": "Tracking the time since the last release or version was made available offers insights into the project's update cadence. Frequent releases suggest the project is actively delivering new features and improvements, while infrequent releases could mean the project is not a high priority.",
                "weight": weights.TIME_SINCE_LAST_RELEASE_WEIGHT
            },

            "forks_count": {
                "value": forks_count,
                "score": None,
                "title": "Number of Forks",
                "description": "Assessing a project's popularity by combining its number of stars and forks provides a measure of community engagement and trust. High popularity indicates that many developers are interested in using, contributing to, or adapting the project, which can enhance its security through broader scrutiny and more active maintenance.",
                "weight": None
            },
            "popularity": {
                "value": stargazers_count + forks_count ,
                "score": final_dict["popularity_score"],
                "title": "Popularity",
                "description": "Assessing a project's popularity by combining its number of stars and forks provides a measure of community engagement and trust. High popularity indicates that many developers are interested in using, contributing to, or adapting the project, which can enhance its security through broader scrutiny and more active maintenance.",
                "weight": weights.POPULARITY_WEIGHT
            },
            "stargazers_count": {
                "value": stargazers_count,
                "score": None,
                "title": "Number of Stargazers",
                "description": "some description",
                "weight": None
            },
            #"is_dependabot": {
                #"value": is_dependabot,
                #"score": final_dict["is_dependabot_score"],
                #"title": "Using Dependabot",
                #"description": "The presence of Dependabot, a tool that automatically creates pull requests to update dependencies and address security vulnerabilities, suggests the project is proactively managing its dependencies and addressing security concerns.",
                #"weight": weights.IS_DEPENDABOT_WEIGHT
            #},
            "is_security_md": {
                "value": is_security_md,
                "score": final_dict["is_security_md_score"],
                "title": "Existence of security.md",
                "description": "The existence of a security.md file, can provide valuable information about the project's security practices, vulnerability disclosure policies, and security-related best practices.",
                "weight": weights.IS_SECURITY_MD_WEIGHT
            },
            "avg_time_for_issue": {
                "value": avg_time_for_issue,
                "score": final_dict["average_issue_wait_time_score"],
                "title": "Average amount of days until an issue is fixed",
                "description": "The average number of days it takes for the project maintainers to fix reported bugs or issues can reveal how responsive and efficient the project is in addressing user concerns. A low average number of days to fix bugs suggests the project is dedicated to providing a reliable and well-maintained experience.",
                "weight": weights.AVERAGE_ISSUE_WAIT_TIME_WEIGHT
            },
            "avg_time_to_merge": {
                "value": avg_time_to_merge,
                "score": final_dict["average_pr_wait_time_score"],
                "title": "Average amount of days until a merge request is solved",
                "description": "The average number of days it takes for the project maintainers to merge pull requests or contributions from the community reflects the project's openness and responsiveness to community involvement. A low average number of days to merge suggests the project values and encourages external contributions.",
                "weight": weights.AVERAGE_PR_WAIT_TIME_WEIGHT
            },
            "dependencies": {
                "value": total_dependencies,
                "score": final_dict["dependency_score"],
                "title": "Number of dependencies",
                "description": "The total number of dependencies indicates that there is a high chance of transitive vulnerabilities within the project",
                "weight": weights.DEPENDENCY_AMOUNT_WEIGHT
            },
            "final_score" : final_dict["final_score"]
        })


    except requests.exceptions.RequestException as e:
        print("error while fetching data: ", e)
        return None



#---------------TESTING AREA----------------

url = "https://github.com/phidatahq/phidata"
url2 = "https://github.com/Stp1t/rift-vision"
url3 = "https://github.com/zmh-program/chatnio"
url4 = "https://github.com/nodejs/node"
url5 = "https://github.com/graphql/graphql-spec"
url6 = "https://github.com/golang/go"


if __name__ == '__main__':
    info = get_github_repo_info(url6)
    print(info)
