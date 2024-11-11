<script lang="ts">
	import '../app.css';
	import { ModeWatcher } from 'mode-watcher';
	import Theme_switch from '$lib/components/ui/Theme_switch.svelte';
	import CircleUser from 'lucide-svelte/icons/circle-user';
	import Menu from 'lucide-svelte/icons/menu';
	import Search from 'lucide-svelte/icons/search';
	import SearchCode from 'lucide-svelte/icons/search-code';
	import Shield from 'lucide-svelte/icons/shield';
	import { browser } from '$app/environment';
	import { Button } from '$lib/components/ui/button/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import * as Sheet from '$lib/components/ui/sheet/index.js';

	// import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import { page, navigating } from '$app/stores';
	import { capitalize } from '$lib/strings';
	import { Toaster } from '$lib/components/ui/sonner';
	import { toast } from 'svelte-sonner';
	import { onMount } from 'svelte';
	import type { Readable } from 'svelte/store';
	let breadcrumbs: string[] = [];
	$: breadcrumbs = $page.url.pathname.slice(1).split('/');
	type navItem = { text: string; path: string };
	let navItems: navItem[] = [
		{ text: 'Home', path: '/' },
		{ text: 'About', path: '/about' }
	];
	let open = false;
	$: if ($navigating) open = false;
</script>

<svelte:head>
	<title>
		{$page?.url?.pathname != '/' ? `${capitalize($page?.url?.pathname?.slice(1))}` : 'Home'} | Safos
	</title>
</svelte:head>
<ModeWatcher />
<div class="flex min-h-screen w-full flex-col">
	<header class="sticky top-0 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
		<nav
			class="hidden flex-col gap-6 text-lg font-medium md:flex md:flex-row md:items-center md:gap-5 md:text-sm lg:gap-6"
		>
			<a href="/" class="flex items-center gap-2 text-lg font-semibold md:text-base">
				<Shield class="h-6 w-6" />
				<span class="hidden lg:block">Safos</span>
			</a>
			{#each navItems as navItem}
				<a
					href={navItem.path}
					class="{$page.url.pathname === navItem.path
						? 'text-foreground'
						: 'text-muted-foreground'} px-2 py-4 transition-colors hover:text-foreground"
				>
					{navItem.text}
				</a>
			{/each}
		</nav>
		<Sheet.Root bind:open>
			<Sheet.Trigger asChild let:builder>
				<Button variant="outline" size="icon" class="shrink-0 md:hidden" builders={[builder]}>
					<Menu class="h-5 w-5" />
					<span class="sr-only">Toggle navigation menu</span>
				</Button>
			</Sheet.Trigger>
			<Sheet.Content side="left">
				<nav class="grid gap-6 text-lg font-medium">
					<a href="/" class="flex items-center gap-2 text-lg font-semibold">
						<Shield class="h-6 w-6" />
						<span>Safos</span>
					</a>
					{#each navItems as navItem}
						<a
							href={navItem.path}
							class="{$page.url.pathname === navItem.path
								? 'text-foreground'
								: 'text-muted-foreground'} hover:text-foreground"
						>
							{navItem.text}
						</a>
					{/each}
				</nav>
			</Sheet.Content>
		</Sheet.Root>
		<div class="flex w-full items-center gap-4 md:ml-auto md:gap-2 lg:gap-4">
			<form class="ml-auto flex-1 sm:flex-initial">
				<div class="relative">
					<Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
					<Input
						type="search"
						placeholder="Analyze repository"
						class="pl-8 sm:w-[300px] md:w-[200px] lg:w-[300px]"
					/>
				</div>
			</form>
			<Theme_switch></Theme_switch>
			<!-- 			
			<DropdownMenu.Root>
				<DropdownMenu.Trigger asChild let:builder>
					<Button builders={[builder]} variant="secondary" size="icon" class="rounded-full">
						<CircleUser class="h-5 w-5" />
						<span class="sr-only">Toggle user menu</span>
					</Button>
				</DropdownMenu.Trigger>
				<DropdownMenu.Content align="end">
					<DropdownMenu.Label>My Account</DropdownMenu.Label>
					<DropdownMenu.Separator />
					<DropdownMenu.Item>Settings</DropdownMenu.Item>
					<DropdownMenu.Item>Support</DropdownMenu.Item>
					<DropdownMenu.Separator />
					<DropdownMenu.Item>Logout</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu.Root> -->
		</div>
	</header>
	<main class="flex flex-1 flex-col gap-4 p-4 md:gap-8 md:p-8">
		<slot></slot>
		<Toaster expand={true} richColors></Toaster>
	</main>
</div>

<style></style>
