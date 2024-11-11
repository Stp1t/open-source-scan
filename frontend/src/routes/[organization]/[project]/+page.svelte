<script lang="ts">
	import ChevronLeft from 'lucide-svelte/icons/chevron-left';
	import Check from 'lucide-svelte/icons/check';
	import X from 'lucide-svelte/icons/x';
	import UsersRound from 'lucide-svelte/icons/users-round';
	import Package from 'lucide-svelte/icons/package';
	import MessagesSquare from 'lucide-svelte/icons/messages-square';
	import GitFork from 'lucide-svelte/icons/git-fork';
	import LoaderCircle from 'lucide-svelte/icons/loader-circle';
	import Star from 'lucide-svelte/icons/star';
	import type { GeneralRepositoryInfo, MetricResult, MetricsResults } from '$lib/types';
	import Countup from 'svelte-countup';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	import { goto } from '$app/navigation';
	import { writable, derived } from 'svelte/store';
	import { toast } from 'svelte-sonner';
	export let data;
	import { page } from '$app/stores';
	import * as Avatar from '$lib/components/ui/avatar';
	import { Progress } from '$lib/components/ui/progress';
	import { messages, clientKey } from '$lib/state/sse';
	import { source } from 'sveltekit-sse';
	import type { Readable } from 'svelte/store';
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	let messageListener: Readable<string> | null;
	let generalRepositoryInfo: GeneralRepositoryInfo = {
		description: '',
		amountContributors: 0,
		stars: 0,
		discussions: 0,
		usedBy: 0,
		forks: 0
	};
	let metricsResult: MetricResult[] = [
		// {
		// 	title: 'Amount of releases',
		// 	weight: 10,
		// 	description:
		// 		'Tracking the total number of releases or versions made available provides insight into how actively the project is being developed. Frequent releases indicate the project is delivering new features and bug fixes to users, whereas infrequent releases may signal a lack of active maintenance.',
		// 	value: true,
		// 	score: 80
		// }
	];
	console.log('Pagedata', data);
	console.log($page.url.pathname);
	let totalScore = 0;
	// $: console.log($messageListener);
	let loading: boolean = true;
	$: if ($messageListener) {
		try {
			const { message } = JSON.parse($messageListener);
			loading = false;
			totalScore = message.final_score * 100;
			console.log(totalScore, message.final_score);
			generalRepositoryInfo = {
				forks: message.forks_count.value ?? 0,
				description: message.description,
				amountContributors: message.contributors.value ?? 0,
				stars: message.stargazers_count.value ?? 0,
				picture_url: message.picture_url
			};
			console.log(message);
			delete message.repo_name;
			delete message.owner;
			delete message.final_score;
			delete message.stargazers_count;
			delete message.forks_count;
			delete message.description;
			delete message.picture_url;

			metricsResult = Object.values(message);
			metricsResult = metricsResult.sort((a, b) => a.score - b.score);
			metricsResult = metricsResult.map((metric) => ({
				...metric,
				score: Math.round(metric.score * 100),
				weight: metric.weight * 100
			}));
			console.log(metricsResult);
		} catch (e) {
			console.error('ERROR', e);
		}
	}
	onMount(async () => {
		if (browser) {
			const getKeyResponse = await fetch('/sse/request-key', {
				headers: {
					Accept: 'application/json',
					'Content-Type': 'application/json'
				}
			});

			if (getKeyResponse.status >= 300) {
				console.log(getKeyResponse.status, 'Failed reading stream.');
			} else {
				const { key }: { key: string } = await getKeyResponse.json();
				clientKey.set(key);
				messageListener = source(`/sse/${$clientKey}/read`).select($page.url.pathname);
				console.log('Reading stream successfully.');
			}
		}
	});
</script>

<svelte:head>
	<title>Analysis Result | Safos</title>
</svelte:head>
<form method="POST">
	<div class="mx-auto grid max-w-[100rem] flex-1 auto-rows-max gap-4">
		<div class="flex items-center gap-4">
			<Button variant="outline" size="icon" class="h-7 w-7" href="/">
				<ChevronLeft class="h-12 w-12" />
				<span class="sr-only">Back</span>
			</Button>
			<h1 class="flex-1 shrink-0 whitespace-nowrap text-xl font-semibold tracking-tight sm:grow-0">
				<span class="font-bold">Analysis Result</span>
			</h1>
		</div>
		<div class="grid gap-4 md:grid-cols-[1fr_250px] lg:grid-cols-8 lg:gap-8">
			<div id="totalScore" class="col-span-2 flex flex-col justify-center gap-4 lg:gap-8">
				{#if !loading}
					<!-- <Progress value={totalScore}></Progress>  -->
					<div>
						<h2 class="text-slate-800 dark:text-slate-400">Total score</h2>
						<p
							class="w-full text-center text-9xl font-extrabold"
							class:text-red-500={totalScore < 50}
							class:text-yellow-500={totalScore >= 50 && totalScore < 75}
							class:text-green-500={totalScore >= 75 && totalScore <= 100}
						>
							<Countup value={totalScore} duration={1000} /><span
								class="text-2xl text-slate-800 dark:text-slate-400">/100</span
							>
						</p>
					</div>
				{:else}
					<h2 class="text-slate-800 dark:text-slate-400">
						<Skeleton class="h-4 w-[150px]"></Skeleton>
					</h2>
					<div class="flex w-full items-center justify-center text-center text-9xl font-extrabold">
						<Skeleton class="h-24 w-24 rounded-3xl"></Skeleton>
					</div>
				{/if}
			</div>
			<div
				id="generalRepoInformation"
				class="col-span-6 grid auto-rows-max items-start gap-4 lg:gap-8"
			>
				<Card.Root>
					<Card.Header>
						<Card.Title class="relative flex justify-between text-4xl">
							{$page.params.organization}/{$page.params.project}
							{#if !loading}
								<Avatar.Root class="absolute right-0 h-12 w-12">
									<Avatar.Image src={generalRepositoryInfo.picture_url} alt="Project logo" />
									<Avatar.Fallback>{$page.params.project.charAt(0).toUpperCase()}</Avatar.Fallback>
								</Avatar.Root>
							{:else}
								<Skeleton class="absolute right-0 h-12 w-12 rounded-full"></Skeleton>
							{/if}
						</Card.Title>
						<Card.Description class="text-xl"
							>{#if !loading}{generalRepositoryInfo.description}{:else}
								<Skeleton class="mt-4 h-4 w-[500px]"></Skeleton>{/if}</Card.Description
						>
					</Card.Header>
					<Card.Content>
						<div class="flex justify-between">
							{#if !loading}
								<div class="flex gap-4">
									<UsersRound></UsersRound>
									{generalRepositoryInfo.amountContributors}
									<span class="text-slate-800 dark:text-slate-400">Contributors</span>
								</div>
								{#if generalRepositoryInfo.usedBy}
									<div class="flex gap-4">
										<Package></Package>
										{generalRepositoryInfo.usedBy}
										<span class="text-slate-800 dark:text-slate-400">Used By</span>
									</div>
								{/if}
								{#if generalRepositoryInfo.discussions}
									<div class="flex gap-4">
										<MessagesSquare></MessagesSquare>
										{generalRepositoryInfo.discussions}
										<span class="text-slate-800 dark:text-slate-400">Discussions</span>
									</div>
								{/if}
								<div class="flex gap-4">
									<Star></Star>
									{generalRepositoryInfo.stars}
									<span class="text-slate-800 dark:text-slate-400">Stars</span>
								</div>
								<div class="flex gap-4">
									<GitFork></GitFork>
									{generalRepositoryInfo.forks}
									<span class="text-slate-800 dark:text-slate-400">Forks</span>
								</div>
							{:else}
								<Skeleton class="h-4 w-[250px]"></Skeleton>
								<Skeleton class="h-4 w-[250px]"></Skeleton>
								<Skeleton class="h-4 w-[250px]"></Skeleton>
							{/if}
						</div></Card.Content
					>
				</Card.Root>
			</div>
		</div>
		<hr class="my-8" />
		<!-- <h2 class="text-slate-800 dark:text-slate-400">Detailed results:</h2> -->
		<h2 class="font-semibold text-black dark:text-white">Detailed results:</h2>
		{#if !loading}
			{#each metricsResult as metric}
				<Card.Root>
					<Card.Header>
						<Card.Title class="flex text-2xl"
							>{metric.title}:
							<span class="ml-4 flex flex-row">
								{#if typeof metric.value === 'number'}
									{Math.round(metric.value)}
								{:else if typeof metric.value === 'boolean'}
									{#if metric.value}
										Yes <Check
											class="ml-2 mt-1 h-6 w-6 rounded bg-green-200 text-green-600 dark:bg-green-400 dark:text-green-900"
										></Check>
									{/if}
								{:else if typeof metric.value === 'undefined' || metric.value === null}
									-
								{/if}
							</span></Card.Title
						>
					</Card.Header>
					<Card.Content class="flex gap-8">
						<p class="w-full">
							{metric.description}
						</p>
						<div>
							<p
								class="px-8 text-6xl font-semibold"
								class:text-red-500={metric.score < 50}
								class:text-yellow-500={metric.score >= 50 && metric.score < 75}
								class:text-green-500={metric.score >= 75 && metric.score <= 100}
							>
								{metric.score}<span class="text-xl dark:text-white text-black">/100</span>
							</p>
							<p
								class="w-full -translate-y-4 text-center text-sm text-slate-800 dark:text-slate-400"
							>
								Weight: {metric.weight}%
							</p>
						</div>
					</Card.Content>
				</Card.Root>{/each}
		{:else}
			{#each { length: 5 } as index}
				<Card.Root>
					<Card.Header>
						<Card.Title class="relative flex justify-between text-4xl">
							<Skeleton class="h-8 w-[400px]"></Skeleton>
						</Card.Title>
					</Card.Header>
					<Card.Content class="align-center flex items-center justify-between">
						<Skeleton class="h-4 w-[1000px]"></Skeleton>
						<Skeleton class=" h-20 w-20 -translate-y-8 rounded-full"></Skeleton>
					</Card.Content>
				</Card.Root>
			{/each}
		{/if}
		<div class="flex items-center justify-center gap-2 md:justify-end"></div>
	</div>
</form>
