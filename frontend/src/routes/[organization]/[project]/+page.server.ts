import type { PageServerLoad } from './$types';
export const load: PageServerLoad = async ({ params }) => {
	console.log(params.organization, params.project)
	const job_trigger_result = await fetch(new URL(`/${params.organization}/${params.project}`, "http://localhost:5000"), {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json'
		}
	})
		.then(async (response) => {
			return response.json()
		})
		.catch((error) => {
			console.error('Error loading analysis results:', error);
			//return new Response(JSON.stringify({ "error": error }), { status: 500 });
			return {}
		});
	return job_trigger_result
};