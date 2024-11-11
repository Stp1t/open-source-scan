import { cachedEmitters } from '$lib/state/sse';
import { error } from '@sveltejs/kit';

export async function POST({ request, params }) {
    const { key } = params;
    if (!key) {
        error(400, 'Bad request, no key provided.')
    }
    const message = await request.json();
    console.log(message)
    if (!message) {
        error(400, 'Bad request, no message provided')
    }
    const channel = `/${message.owner}/${message.repo_name}`
    const writeToAll: boolean = key.toLowerCase() === "all"
    if (writeToAll) {
        const emitters = Array.from(cachedEmitters.values());
        if (!emitters) {
            error(404, 'No emitters found.');
        }
        for (const emit of emitters) {
            emit(channel, JSON.stringify({ message }));
        }
    } else {
        const emit = cachedEmitters.get(key);
        if (!emit) {
            error(401, 'Unauthorized, provided emitter key is not valid.');
        }

        emit(channel, JSON.stringify(message));
    }
    const response = new Response("", { status: 200 });

    return response;
}

