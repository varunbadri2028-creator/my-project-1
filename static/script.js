const output = document.getElementById("output");
const audioPlayer = document.getElementById("audioPlayer");

window.onload = () => greetUser();

function greetUser() {
    const lang = document.getElementById("language").value;

    fetch("/greet", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({lang})
    })
    .then(res => res.json())
    .then(data => {
        output.innerText = data.text;
        if (data.audio) playAudio(data.audio);
    });
}

function analyzeText() {
    const text = document.getElementById("userText").value;
    const lang = document.getElementById("language").value;

    if (!text) return alert("Please type something");

    fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text, lang})
    })
    .then(res => res.json())
    .then(data => {
        output.innerText = data.text;
        if (data.audio) playAudio(data.audio);
    });
}

function playAudio(url) {
    audioPlayer.src = url;
    audioPlayer.load();
    audioPlayer.oncanplaythrough = () => {
        audioPlayer.play().catch(err => console.log("Browser blocked autoplay"));
    };
}

function startMic() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return alert("Speech recognition not supported");

    const lang = document.getElementById("language").value;
    const recognition = new SpeechRecognition();

    recognition.lang = lang === "hi" ? "hi-IN" :
                       lang === "te" ? "te-IN" :
                                        "en-IN";

    recognition.start();

    recognition.onresult = evt => {
        document.getElementById("userText").value = evt.results[0][0].transcript;
    };
}