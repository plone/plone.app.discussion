jq(document).ready(function() {

    /*****************************************************************
     * Hide the reply and the cancel button for the regular add
     * comment form.
     *****************************************************************/
    jq(".reply").find("input[name='form.buttons.reply']").css("display", "none");
    jq(".reply").find("input[name='form.buttons.cancel']").css("display", "none");


    /*****************************************************************
     * If a reply-to-comment form was submitted (in_reply_to field was
     * set in the request), create a reply-to-comment form right under
     * the comment.
     *****************************************************************/
    var post_comment_div = jq("#commenting");
    var in_reply_to_field = post_comment_div.find("input[name='form.widgets.in_reply_to']");
    if (in_reply_to_field.val() != "") {
        var current_reply_id = "#" + in_reply_to_field.val();
        var current_reply_to_div = jq(".discussion").find(current_reply_id);
        createReplyForm(current_reply_to_div);
        clearForm(post_comment_div);
    }

    /*****************************************************************
     * Remove the z3c.form error messages and all input values from a
     * form.
     *****************************************************************/
    function clearForm(form_div) {
        form_div.find(".error").removeClass("error");
        form_div.find(".fieldErrorBox").remove();
        form_div.find("input[type='text']").attr("value", "")
        form_div.find("textarea").attr("value", "")
    }

    /*****************************************************************
     * Create a reply-to-comment form right under the comment_div.
     *****************************************************************/
    function createReplyForm(comment_div){

        var comment_id = comment_div.attr("id");

        var reply_button = comment_div.find(".reply-to-comment-button");

        /* Clone the reply div at the end of the page template that contains
         * the regular comment form.
         */
        var reply_div = jq("#commenting").clone(true);

        /* Remove the ReCaptcha JS code before appending the form. If not
         * removed, this causes problems
         */
        reply_div.find("#formfield-form-widgets-captcha").find("script").remove();

        /* Insert the cloned comment form right after the reply button of the
         * current comment.
         */
        reply_div.appendTo(comment_div).css("display", "none");

        /* Remove id="reply" attribute, since we use it to uniquely
           the main reply form. */
        reply_div.removeAttr("id")

        /* Hide the reply button (only hide, because we may want to show it
         * again if the user hits the cancel button).
         */
        jq(reply_button).css("display", "none");

        /* Fetch the reply form inside the reply div */
        var reply_form = reply_div.find("form");

        /* Populate the hidden 'in_reply_to' field with the correct comment id */
        reply_form.find("input[name='form.widgets.in_reply_to']").val(comment_id);

        /* Add a remove-reply-to-comment Javascript function to remove the form */
        var cancel_reply_button = reply_div.find(".cancelreplytocomment");
        cancel_reply_button.attr("id", comment_id);

        /* Show the cancel buttons. */
        reply_form.find("input[name='form.buttons.cancel']").css("display", "inline");

        /* Show the reply layer with a slide down effect */
        reply_div.slideDown("slow");

        /* Show the cancel button in the reply-to-comment form */
        cancel_reply_button.css("display", "inline");
    }

    /*****************************************************************
     * Show the reply button only when Javascript is enabled.
     * Otherwise hide it, since the reply functions rely on jQuery.
     *****************************************************************/
    jq(".reply-to-comment-button").css("display" , "inline");


    /*****************************************************************
     * Create reply to comment form.
     *****************************************************************/
    jq(".reply-to-comment-button").bind("click", function(e){
        var comment_div = jq(this).parents().filter(".comment");
        createReplyForm(comment_div);
        clearForm(comment_div);
    });

    /*****************************************************************
     * Remove reply to comment form.
     *****************************************************************/
    jq("#form-buttons-cancel").bind("click", function(e){
        e.preventDefault();
        reply_to_comment_button = jq(this).parents().filter(".comment").find(".reply-to-comment-button");

        /* Find the reply-to-comment form and hide and remove it again. */
        reply_to_comment_form = jq(this).parents().filter(".reply")
        reply_to_comment_form.slideUp("slow", function() { jq(this).remove(); } );

        /* Show the reply-to-comment button again. */
        reply_to_comment_button.css("display", "inline");

    });

    /*****************************************************************
     * Remove comment.
     *****************************************************************/
    /*
    jq("input[name='form.button.DeleteComment']").click(function(e){
        e.preventDefault();
        var form = jq(this).parent();
        var target = jq(form).attr("action");
        var comment = jq(form).parent();
        var reply_comments = jq(comment).find("~ .comment:not(.replyTreeLevel0 ~ div)");
        reply_comments.css("background", "red");
        jq.ajax({
            type: "GET",
            url: target,
            success: function(msg){
                // fade out row
                jq(comment).fadeOut("normal", function(){
                    jq(this).remove();
                });
            },
            error: function(msg){
                alert("Error sending AJAX request:" + target);
            },
        });
    });
    */

    /*****************************************************************
     * Publish comment.
     *****************************************************************/
    /*
    jq("input[name='form.button.PublishComment']").click(function(e){
        e.preventDefault();
        var button = jq(this);
        var form = jq(this).parent();
        var target = jq(form).attr("action");
        var comment = jq(form).parent()
        jq.ajax({
            type: "GET",
            url: target,
            success: function(msg){
                // fade out row
                jq(button).fadeOut("normal", function(){
                    jq(form).remove();
                });
            },
            error: function(msg){
                alert("Error sending AJAX request:" + target);
            },
        });
    });
    */
 });