jq(document).ready(function() {

    jq(".reply").find("input[name='form.buttons.reply']").css("display", "none");

    /*****************************************************************
     * Show the reply button only when Javascript is enabled.
     * Otherwise hide it, since the reply functions relies on jQuery.
     *****************************************************************/
    jq(".reply-to-comment-button").css("display" , "inline");


    /*****************************************************************
	 * Create reply to comment form.
     *****************************************************************/
	jq(".reply-to-comment-button").bind("click", function(e){

		var comment_div = jq(this).parents().filter(".comment");
		var comment_id = comment_div.attr("id");

		var reply_button = comment_div.find(".reply-to-comment-button");

	    /* Clone the reply div at the end of the page template that contains
	     * the regular comment form and insert it after the reply button of the
	     * current comment.
	     */
	    var reply_div = jq("#commenting").clone(true);
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

        /* Remove already typed in text from the reply form. */
        reply_form.find(".field").find("input").attr("value", "")
        reply_form.find(".field").find("textarea").attr("value", "")

        /* Populate the hidden 'in_reply_to' field with the correct comment id */
		reply_form.find("input[name='form.widgets.in_reply_to']").val(comment_id);

	    /* Add a remove-reply-to-comment Javascript function to remove the form */
	    var cancel_reply_button = reply_div.find(".cancelreplytocomment");
	    cancel_reply_button.attr("id", comment_id);

        /* Hide the comment button and show the reply button
         * in the reply-to-comment forms */
        reply_form.find("input[name='form.buttons.comment']").css("display", "none");
        reply_form.find("input[name='form.buttons.reply']").css("display", "inline");

	    /* Show the reply layer with a slide down effect */
	    reply_div.slideDown("slow");

	    /* Show the cancel button in the reply-to-comment form */
	    cancel_reply_button.css("display", "inline");

    });


    /*****************************************************************
     * Remove reply to comment form.
     *****************************************************************/
    jq(".cancelreplytocomment").bind("click", function(e){

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