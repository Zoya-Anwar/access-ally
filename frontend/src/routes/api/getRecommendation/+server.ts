import http from 'http';

export async function POST({ request }: { request: any }) {
  const flaskServerUrl = 'http://127.0.0.1:5000'; // Include the port number
  const flaskEndpoint = '/api/card_data'; // Replace with your Flask server endpoint

  const payload = {
    // Define the data you want to send to your Flask server
    key: 'value', // Modify this to match the expected data structure of your Flask server
    ...await request.json(), // Include any parameters you want to send from the client
  };

  const requestOptions = {
    hostname: '127.0.0.1',
    port: 5000,
    path: flaskEndpoint,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  };

  return new Promise<Response>((resolve) => {
    const req = http.request(requestOptions, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        if (res.statusCode !== 200) {
          resolve(new Response('Error: Unable to get data from Flask server', { status: res.statusCode }));
        } else {
          // Assuming the Flask server returns JSON data, you can return it directly
          try {
            const jsonData = JSON.parse(data);
            resolve(new Response(JSON.stringify(jsonData), {
              headers: { 'Content-Type': 'application/json' },
            }));
          } catch (error) {
            resolve(new Response('Error: Unable to parse data from Flask server', { status: 500 }));
          }
        }
      });
    });

    req.on('error', (error) => {
      resolve(new Response('Error: Unable to communicate with Flask server', { status: 500 }));
    });

    req.write(JSON.stringify(payload));
    req.end();
  });
}

