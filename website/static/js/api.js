'use strict';

function addMessage(date, text, style) {
    let message = 
        "<li class=\"alert " + style + " d-flex\">" +
        "   <span class=\"text-muted mr-2\">" + date + "</span>" + 
        "   <span class=\"website-message-text\">" + text + "</span>"+
        "</li>";
    $(message).hide().prependTo("#message-history").slideDown("fast");
}

function addNicknameMessage(date, text) {
    addMessage(date, text, "website-message");
}

function addWarningMessage(date, text) {
    addMessage(date, text, "website-warn-message");
}

function addErrorMessage(date, text) {
    addMessage(date, text, "website-error-message");
}

function updateUsername(username, successCallback, warningCallback, errorCallback) {
    $.ajax({
        url: '/api/username-chat/',
        dataType: 'json',
        type: 'POST',
        data: {
            'csrfmiddlewaretoken': getCookie('csrftoken'),
            'username': username
        },
        success: function(data, textStatus, xhr) {
            console.log(textStatus, data)
            let date = data["date"];
            let status = data["status"];
            let type = data["type"];
            let text = data["text"];

            if (status === "success") {
                successCallback(date, type, text);
            } else if (status === "warning") {
                warningCallback(date, type, text);
            } else {
                errorCallback(date, type, text);
            }
        },
        error: function(xhr, textStatus, errorThrown) {
            errorCallback("now", textStatus, errorThrown);
        },
        xhrFields: {
            withCredentials: true
        },
        async: false
    });
}


$(document).ready(function() {
    $("#set-original-nickname").click(function() {
        let originalNickname = $("#original-nickname").text();
        $("#nickname").val(originalNickname);
    });

    $("#update-nickname").click(function() {
        let error = $("#nickname-error");
        let hint = $("#nickname-hint");
        let info = $("#nickname-info");

        error.hide();
        hint.hide();
        info.hide();

        let nicknameElement = $("#nickname");
        let nickname = nicknameElement.val();

        updateUsername(nickname, 
            function(date, successType, newNickname) {
                nicknameElement.css("border-color", INFO_COLOR);
                nicknameElement.val("");
                info.text(successType);
                info.show();

                addNicknameMessage(date, nickname);
            },

            function(date, warningType, warningText) {
                nicknameElement.css("border-color", WARN_COLOR);
                hint.text(warningType);
                hint.show();

                addWarningMessage(date, warningText);
            },

            function(date, errorType, errorText) {
                nicknameElement.css("border-color", ERROR_COLOR);
                error.text(errorType);
                error.show();

                addErrorMessage(date, errorText);
            }
        );
    });
});