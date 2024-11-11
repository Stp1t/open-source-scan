<script lang="ts">
	import SearchCode from 'lucide-svelte/icons/search-code';
	import { Button } from '$lib/components/ui/button/index.js';
	import { parseGithubUrl } from '$lib/urls.js';

	import Shield from 'lucide-svelte/icons/shield';
	import { Input } from '$lib/components/ui/input/index.js';
	import { goto } from '$app/navigation';
	import { writable, derived } from 'svelte/store';
	import type { PageData } from './$types.js';
	export let data: PageData;
	import { page } from '$app/stores';
	type item = {
		value: string;
		label: string;
	};

	let initialFormData: { search: string | null } = {
		search: ''
	};
	let formData = writable(structuredClone(initialFormData));
	const formIsValid = derived(formData, ($formData) => {
		let requiredFields = [$formData.search];
		return requiredFields.includes('');
	});

	async function submit(e: Event) {
		console.log('submitted');
		if (!$formData.search || $formData.search.trim() === '') {
			e.preventDefault();
			return;
		}
		const target = parseGithubUrl($formData.search);
		if (!target) {
			e.preventDefault();
			return;
		}
		// const searchParams = new URLSearchParams({ q: encodeURIComponent(target.pathname) });
		// goto(`/analysis?${searchParams.toString()}`);
		// goto(target.pathname);
		console.log(target.pathname);
		goto(target.pathname);
	}
</script>

<svelte:head>
	<title>Home | Safos</title>
</svelte:head>

<div class="mx-auto flex h-screen items-center justify-center">
	<div class="grid max-w-[100rem] auto-rows-max gap-4">
		<div class="flex flex-col items-center gap-4">
			<Shield class=" text-slate-100 dark:text-slate-800" size="256"></Shield>
			<h1
				class="flex-1 shrink-0 whitespace-nowrap text-8xl font-semibold uppercase tracking-tight sm:grow-0"
			>
				<span class="text-primary">Scan</span> a repo
			</h1>
			<h2 class="flex-1 shrink-0 whitespace-nowrap text-4xl font-semibold tracking-tight sm:grow-0">
				Enter a URL to a GitHub repository or enter a project name to calculate a security score
			</h2>
		</div>
		<form method="GET" on:submit|preventDefault={submit}>
			<div class="grid gap-4 md:grid-cols-[1fr_250px] lg:grid-cols-3 lg:gap-8">
				<div class="col-span-full grid auto-rows-max items-start gap-4 lg:gap-8">
					<div class="mt-8 flex items-center justify-center">
						<Input
							id="description"
							type="search"
							class="h-8 w-full rounded-full bg-slate-200 px-4 py-8 text-4xl leading-4 dark:bg-slate-900"
							placeholder="e.g. 'https://github.com/nodejs/node'"
							bind:value={$formData.search}
						/>

						<Button
							type="submit"
							disabled={$formData.search === ''}
							on:click={submit}
							class="mx-4 rounded-full py-10 text-4xl hover:px-4"
						>
							<span class="sr-only">Analyze repository</span>
							<SearchCode class="h-14 w-14"></SearchCode>
						</Button>
					</div>
				</div>
			</div>
		</form>
	</div>
</div>
