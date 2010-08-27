

module("comments", {
    setup: function () {
        // Create a comments section with one comment inside
        var comments = $(document.createElement("div"))
            .addClass("discussion")
            .append($(document.createElement("div"))
                .addClass("comment")
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
                    .addClass("formfield-form-widgets-in_reply_to")
                    .append($(document.createElement("input"))
                        .attr("name", "form.widgets.in_reply_to")
                        .val("")        
                    )
                )
                .append($(document.createElement("div"))
                    .addClass("formfield-form-widgets-author_name")
                    .append($(document.createElement("input"))
                        .attr("name", "form.widgets.author")                        
                        .attr("type", "text")
                    )
                )
                .append($(document.createElement("div"))
                    .addClass("formfield-form-widgets-text")
                    .append($(document.createElement("textarea"))
                        .attr("name", "form.widgets.text")
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
        $(".discussion").remove();
    }
});


test("Initialisation", function() {
    expect(1);
    ok($.discussion, "$.discussion");
});

test("Hide the reply and the cancel button for the comment form", function(){
    expect(1);
    $(".reply").find("input[name='form.buttons.cancel']").css("display", "none");
    equals($("input[name='form.buttons.cancel']").css("display"), "none", "The cancel button should be hidden");
});

test("Show the reply button only when Javascript is enabled", function(){
    expect(1);
    $(".reply-to-comment-button").css("display", "inline");
    equals($("button[class='reply-to-comment-button']").attr("style"), "display: inline;", "The reply button should show up when Javascript is enabled");
});

test("Create a comment reply form.", function() {
    expect(2);
    var comment_div = $("#1282720906349675");
    $.discussion.createReplyForm(comment_div);
    var reply_form = comment_div.find(".reply");
    ok(reply_form, "Reply form has been copied");
    same(reply_form.find("input[name='form.widgets.in_reply_to']").val(), "1282720906349675", "The reply for should have the id of the comment in the in_reply_to field");
});

test("Clear all form values from a form.", function() {
    // Create a reply form with some values
    var comment_div = $("#1282720906349675");
    $.discussion.createReplyForm(comment_div);
    var reply_form = comment_div.find(".reply");
    var author = reply_form.find("input[name='form.widgets.author']");
    var text = comment_div.find("input[name='form.widgets.text']");
    author.val("my author");
    text.val("my text");
    // Call the clearForm function to clear the form
    $.discussion.clearForm(comment_div);
    // Check if all form fields have been cleared
    var author = comment_div.find("input[name='form.widgets.author']");
    var text = comment_div.find("input[name='form.widgets.text']");
    equals(author.val(), "", "The author form value should be empty");
    equals(text.text(), "", "The text form value should be empty");
});

