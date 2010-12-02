/******************************************************************************
 *
 * jQuery functions for the plone.app.discussion comment viewlet and form.
 *
 ******************************************************************************/
(function ($) {
	// This unnamed function allows us to use $ inside of a block of code
	// without permanently overwriting $.
	// http://docs.jquery.com/Using_jQuery_with_Other_Libraries
	    
    //#JSCOVERAGE_IF 0

    /**************************************************************************
     * Window Load Function: Executes when complete page is fully loaded,
     * including all frames,
     **************************************************************************/
    $(window).load(function () {

        /**********************************************************************
         * If the user hits the "clear" button of an open reply-to-comment form,
         * remove the form and show the "reply" button again.
         **********************************************************************/
        $("input[name='form.widgets.globally_enabled:list']").bind("change", function (e) {
            if ($(this).attr("checked")) {
                // enable commenting globally
                $('#formfield-form-widgets-anonymous_comments').removeClass('unclickable');
                $('#formfield-form-widgets-text_transform').removeClass('unclickable');
                $('#formfield-form-widgets-captcha').removeClass('unclickable');
                $('#formfield-form-widgets-show_commenter_image').removeClass('unclickable');
                $('#formfield-form-widgets-moderator_notification_enabled').removeClass('unclickable');
                $('#formfield-form-widgets-user_notification_enabled').removeClass('unclickable');
            } else {
                $('#formfield-form-widgets-anonymous_comments').addClass('unclickable');
                $('#formfield-form-widgets-text_transform').addClass('unclickable');
                $('#formfield-form-widgets-captcha').addClass('unclickable');
                $('#formfield-form-widgets-show_commenter_image').addClass('unclickable');
                $('#formfield-form-widgets-moderator_notification_enabled').addClass('unclickable');
                $('#formfield-form-widgets-user_notification_enabled').addClass('unclickable');
            }
        });    

	});

    //#JSCOVERAGE_ENDIF

}(jQuery));
