/******************************************************************************
 *
 * jQuery functions for the plone.app.discussion comment viewlet and form.
 *
 ******************************************************************************/
(function ($) {
	// This unnamed function allows us to use $ inside of a block of code
	// without permanently overwriting $.
	// http://docs.jquery.com/Using_jQuery_with_Other_Libraries

    /**************************************************************************
     * Disable a control panel setting. Grey out the setting and disable all
     * form elements.
     **************************************************************************/
    $.disableSettings = function (settings) {
        $.each(settings,
               function(intIndex, setting){
                   setting.addClass('unclickable');
                   setting_field = $(setting).find("input,select");
                   setting_field.attr('disabled', 'disabled');
               });          
    };
    
    $.enableSettings = function (settings) {
        $.each(settings,
               function(intIndex, setting){
                   setting.removeClass('unclickable');
                   setting_field = $(setting).find("input,select");
                   setting_field.removeAttr('disabled');
               });    
    };
    	    
    //#JSCOVERAGE_IF 0

    /**************************************************************************
     * Window Load Function: Executes when complete page is fully loaded,
     * including all frames,
     **************************************************************************/
    $(window).load(function () {

        /**********************************************************************
         * If commenting is disabled globally, disable all commenting options.
         **********************************************************************/
        $("input[name='form.widgets.globally_enabled:list']").bind("change", function (e) {
            if ($(this).attr("checked")) {
                // commenting globally enabled
                $.enableSettings([
                    $('#formfield-form-widgets-anonymous_comments'),
                    $('#formfield-form-widgets-text_transform'),
                    $('#formfield-form-widgets-captcha'),
                    $('#formfield-form-widgets-show_commenter_image'),
                    $('#formfield-form-widgets-moderator_notification_enabled'),
                    $('#formfield-form-widgets-user_notification_enabled')
                    ]);
            } else {
                // commenting globally disabled
                $.disableSettings([
                    $('#formfield-form-widgets-anonymous_comments'),
                    $('#formfield-form-widgets-text_transform'),
                    $('#formfield-form-widgets-captcha'),
                    $('#formfield-form-widgets-show_commenter_image'),
                    $('#formfield-form-widgets-moderator_notification_enabled'),
                    $('#formfield-form-widgets-user_notification_enabled'),
                ]);
            }
        });    

	});

    //#JSCOVERAGE_ENDIF

}(jQuery));
