import math
import weights


def contributor_score(c, stars, forks):
    popularity = stars + forks + 1
    expected_contributors = math.log(popularity)

    ratio = c / expected_contributors

    max_ratio = 5
    normalized_ratio = min(ratio / max_ratio, 1)

    score = normalized_ratio
    return round(score, 2)


def commit_score(co, co_max=500):
    score = min(1, co / co_max)
    return round(score,2)

def releases_score(re, re_max=10):
    score = min(1, re / re_max)
    #print(f"releases:{re}")
    #print(f"releases max: {re_max}")
    #print(f"score: {score}")
    return round(score,2)

def popularity_score(fc, sc, p_max=50000):
    p = fc + sc
    score = min(1, math.log(p + 1) / math.log(p_max + 1))
    return round(score,2)

def time_since_last_commit_score(rc, k=0.0025):
    if rc is None:
        return 0
    score = math.exp(-k * rc)
    return round(score,2)

def time_since_last_release_score(tr, k=0.0025):
    if tr is None:
        return 0
    score = math.exp(-k * tr)
    return round(score,2)

def average_issue_wait_time_score(awi, awi_max=50):
    score = 1 / (1 + (awi / awi_max))
    return round(score,2)

def average_pr_wait_time_score(awm, awm_max=50):
    score = 1 / (1 + (awm / awm_max))
    return round(score,2)

def dependency_score(d):
    score = 1 / (1 + (d/100))
    return round(score,2)

def is_dependabot_score(val):
    return 1

def is_security_md_score(val):
    if val:
        return 1
    else:
        return 0




def get_final_score_dict(contributor_amount, commit_amount, fork_amount, star_amount, time_since_last_commit,
                         time_since_last_release, average_issue_wait_time, average_pr_wait_time, dependency_amount, is_dependabot, is_security_md, releases_amount):

    contributor_sc = contributor_score(contributor_amount, star_amount, fork_amount)
    commit_sc = commit_score(commit_amount)
    releases_sc = releases_score(releases_amount)
    popularity_sc = popularity_score(fork_amount, star_amount)
    time_since_last_commit_sc = time_since_last_commit_score(time_since_last_commit)
    time_since_last_release_sc = time_since_last_release_score(time_since_last_release)
    average_issue_wait_time_sc = average_issue_wait_time_score(average_issue_wait_time)
    average_pr_wait_time_sc = average_pr_wait_time_score(average_pr_wait_time)
    dependency_amount_sc = dependency_score(dependency_amount)
    is_dependabot_sc = is_dependabot_score(is_dependabot)
    is_security_md_sc = is_security_md_score(is_security_md)

    final_score = round((
            weights.CONTRIBUTOR_WEIGHT * contributor_sc +
            weights.POPULARITY_WEIGHT * popularity_sc +
            weights.COMMIT_WEIGHT * commit_sc +
            weights.TIME_SINCE_LAST_COMMIT_WEIGHT * time_since_last_commit_sc +
            weights.TIME_SINCE_LAST_RELEASE_WEIGHT * time_since_last_release_sc +
            weights.AVERAGE_ISSUE_WAIT_TIME_WEIGHT * average_issue_wait_time_sc +
            weights.AVERAGE_PR_WAIT_TIME_WEIGHT * average_pr_wait_time_sc +
            weights.DEPENDENCY_AMOUNT_WEIGHT * dependency_amount_sc +
            weights.IS_DEPENDABOT_WEIGHT * is_dependabot_sc +
            weights.IS_SECURITY_MD_WEIGHT * is_security_md_sc +
            weights.RELEASES_WEIGHT * releases_sc
    ),2)

    final_dict = {
        'contributor_score': contributor_sc,
        'commit_score': commit_sc,
        'releases_score':releases_sc,
        'popularity_score': popularity_sc,
        'time_since_last_commit_score': time_since_last_commit_sc,
        'time_since_last_release_score': time_since_last_release_sc,
        'average_issue_wait_time_score': average_issue_wait_time_sc,
        'average_pr_wait_time_score': average_pr_wait_time_sc,
        'dependency_score': dependency_amount_sc,
        'is_dependabot_score': is_dependabot_sc,
        'is_security_md_score': is_security_md_sc,
        'final_score': final_score,
    }

    return final_dict

