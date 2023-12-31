// import { OMDB_API_KEY } from '$env/static/private';
import { json } from '@sveltejs/kit';

export async function POST({ request }: { request: any }) {
	const { title } = await request.json();
	const url = `http://127.0.0.1:8001/card_data`;

	const res = await fetch(url);
	const details = await res.json();
	return json(details);
}
