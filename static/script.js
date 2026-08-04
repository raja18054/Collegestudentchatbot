function sendMessage() {

    let message = document.getElementById("message").value.trim();

    if (message === "") {
        return;
    }

    let chatBox = document.getElementById("chatBox");

    // Show user message
    chatBox.innerHTML += `
        <div class="user">
            ${message}
        </div>
    `;

    fetch("/get_reply", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "message=" + encodeURIComponent(message)
    })
    .then(response => response.json())
    .then(data => {

        chatBox.innerHTML += `
            <div class="bot">
                ${data.reply}
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;

        document.getElementById("message").value = "";

    });

}

// Send message when Enter key is pressed
document.addEventListener("DOMContentLoaded", function () {

    let input = document.getElementById("message");

    if (input) {

        input.addEventListener("keypress", function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                sendMessage();

            }

        });

    }

});
