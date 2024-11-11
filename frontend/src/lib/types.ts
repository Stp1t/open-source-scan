export type GeneralRepositoryInfo = {
    amountContributors: number;
    usedBy?: number;
    discussions?: number;
    stars: number;
    forks: number;
    picture_url?: string;
    description?: string;
}

export type MetricResult = {
    value: boolean | number;
    score: number;
    title: string;
    description: string;
    weight: number;
}

// export type MetricsResults = {
//     amountCommits: MetricResult<number>;
//     amountReleases: MetricResult<number>;
//     amountContributors: MetricResult<number>;
//     amountOpenIssues: MetricResult<number>;
//     timeSinceLastCommit: MetricResult<number>;
//     timeSinceLastRelease: MetricResult<number>;
//     repositoryActivity: MetricResult<number>;
//     dependabotState: MetricResult<boolean>;
//     securitymdState: MetricResult<boolean>;
//     dependencyEvaluation: MetricResult<number>;
//     averageDaysToFixBugs: MetricResult<number>;
//     averageDaysToMerge: MetricResult<number>;
// }