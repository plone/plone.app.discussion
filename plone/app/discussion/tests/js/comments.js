  
module("comments", {
    setup: function () {
        // Create a comments section with one comment inside
        var comments = $(document.createElement("div"))
            .addClass("discussion")
            .append($(document.createElement("div"))
                .addClass("comment replyTreeLevel0 state-published")
                .attr("id", "1282720906349675")
                .append($(document.createElement("div"))
                    .addClass("commentActions"))
                    .append($(document.createElement("button"))
                        .addClass("reply-to-comment-button")
                )
            );
        $(document.body).append(comments);
                
        // Create a basic commenting form
        var commentform = $(document.createElement("div"))
            .append($(document.createElement("form"))
                .addClass("form")
                .append($(document.createElement("div"))
                    .addClass("formfield-form-widgets-author_name")
                    .append($(document.createElement("input"))
                        .addClass("text-widget textline-field")
                        .append($(document.createElement("a"))
                            .addClass("selected")
                            .attr("href", "#fieldsetlegend-default")
                        )
                    )
                )
                .append($(document.createElement("div"))
                    .addClass("formControls")
                    .append($(document.createElement("input"))
                        .attr("name", "form.buttons.comment"))
                    .append($(document.createElement("input"))
                        .attr("name", "form.buttons.cancel"))
                )
            )
            .addClass("reply")
            .attr("id", "commenting");
        $(document.body).append(commentform);
    },
    teardown: function () {
        $("#commenting").remove();
    }
});

test("Hide the reply and the cancel button for the comment form", function () {
    expect(1);
    $(".reply").find("input[name='form.buttons.cancel']")
                .css("display", "none");
    equals($("input[name='form.buttons.cancel']").css("display"), "none", "The cancel button should be hidden");
});

test("Show the reply button only when Javascript is enabled", function () {
    expect(1);
    $(".reply-to-comment-button").css("display" , "inline");    
    equals($("button[class='reply-to-comment-button']").attr("style"), "display: inline;", "The reply button should show up when Javascript is enabled");
});
