function generate() {
    const level = document.getElementById("level").value;

    fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ level })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("content").innerHTML = data.content;

        // audio
        const audio = document.getElementById("audioPlayer");
        audio.src = data.audio;

        // QR
        document.getElementById("qr").innerHTML = "";
        new QRCode(document.getElementById("qr"), {
            text: window.location.origin + data.audio,
            width: 100,
            height: 100
        });
    });
}