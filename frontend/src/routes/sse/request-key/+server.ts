import { cachedKeys } from '$lib/state/sse';

export async function GET() {
  //todo: validate bearer token here.
  const key = crypto.randomUUID();
  cachedKeys.set(key, true);
  // console.log(cachedKeys)
  return new Response(JSON.stringify({ key }));
}