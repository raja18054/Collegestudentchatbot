$(document).ready(function () {

    function sendMessage() {

        var message = $("#message").val().trim();

        if (message === "") return;

        // User message
        $("#chat-box").append(
            '<div class="message user">' + message + '</div>'
        );

        $("#message").val("");

        $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);

        // Typing animation
        $("#typing").show();

        $.post("/get_reply",
        {
            message: message
        },
        function (data) {

            $("#typing").hide();

            // AI reply
            $("#chat-box").append(
                '<div class="message bot">' + data.reply + '</div>'
            );

            $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);

        });

    }

    $("#send").click(function () {
        sendMessage();
    });

    $("#message").keypress(function (e) {

        if (e.which == 13) {

            sendMessage();

        }

    });

});
