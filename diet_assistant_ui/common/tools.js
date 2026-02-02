export async function fetchSSE(url, options, onMessage) {
	const response = await fetch(url, {
		method: "POST",
		headers: options.headers,
		body: new URLSearchParams(options.body)
	});

	const reader = response.body.getReader();
	const decoder = new TextDecoder("utf-8");

	while (true) {
		const {
			value,
			done
		} = await reader.read();
		if (done) break;
		const chunk = decoder.decode(value, {
			stream: true
		});
		// 服务端 SSE 一般格式: "data: xxx\n\n"
		chunk.split("\n\n").forEach(line => {
			if (line.startsWith("data:")) {
				onMessage(line.slice(5));
			}
		});
	}
}