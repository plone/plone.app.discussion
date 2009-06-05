jq(document).ready(function() {
    /* Show the reply-to-comment button only when Javascript is enabled.
     * Otherwise hide it, since the reply functions relies on jQuery.
     */
    jq(".reply-to-comment-button").css("display" , "block");
 });

function createReplyToCommentForm(comment_id) {
    /*
     * This function creates a form to reply to a specific comment with
     * the comment_id given as parameter. It does so by cloneing the existing
     * commenting form at the end of the page template.
     */

    /* The jQuery id of the reply-to-comment button */
    var button = "#reply-to-comment-" + comment_id + "-button";

	/* Clone the reply div at the end of the page template that contains
	 * the regular comment form and insert it after the reply button of the
	 * current comment.
	 */
    reply_div = jq("#commenting").clone(true);
	reply_div.insertAfter(button).css("display", "none")
	reply_div.slideDown("slow");

    /* Remove id="reply" attribute, since we use it to uniquely
       the main reply form. */
    reply_div.removeAttr("id")

    /* Hide the reply button (only hide, because we may want to show it
     * again if the user hits the cancel button).
     */
    jq(button).css("display", "none");

    /* Fetch the reply form inside the reply div */
	reply_form = reply_div.find("form");

    /* Add a hidden field with the id of the comment */
    reply_form.append("<input type=\"hidden\" value=\"" + comment_id + "\" name=\"form.reply_to_comment_id\"");

    /* Change the form action to @@reply-to-comment */
	old_action = reply_form.attr("action");
	new_action = old_action.replace("@@add-comment",  "@@reply-to-comment");
	reply_form.attr("action", new_action);

    /* Add a remove-reply-to-comment Javascript function to remove the form */
	cancel_reply_button = reply_div.find(".cancelreplytocomment");
	cancel_reply_button.attr("onclick", "removeReplyToCommentForm(" + comment_id  +");")

    /* Show the cancel button in the reply-to-comment form */
	cancel_reply_button.css("display", "inline")
}

function removeReplyToCommentForm(comment_id) {
    /*
     * This function removes the reply-to-comment form of a specific comment.
     */

    /* Show the reply-to-comment button again. */
    jq("#reply-to-comment-" + comment_id + "-button").css("display", "block");

	/* Find the reply-to-comment form and hide and remove it again. */
	reply_to_comment_form = jq("#comment-" + comment_id).find(".reply")
	reply_to_comment_form.remove(reply_to_comment_form.slideUp("slow"))
}
