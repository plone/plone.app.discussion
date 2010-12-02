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
        $.each(settings, function (intIndex, setting) {
            setting.addClass('unclickable');
            var setting_field = $(setting).find("input,select");
            setting_field.attr('disabled', 'disabled');
        });          
    };
    
    $.enableSettings = function (settings) {
        $.each(settings, function (intIndex, setting) {
            setting.removeClass('unclickable');
            var setting_field = $(setting).find("input,select");
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
         * Do not allow to change the mail settings if there is no valid mail
         * setup.
         **********************************************************************/
        var invalid_mail_setup = $("#content").hasClass("invalid_mail_setup");
        if (invalid_mail_setup === true) {
            $.disableSettings([
                $('#formfield-form-widgets-moderator_notification_enabled'),
                $('#formfield-form-widgets-user_notification_enabled')
            ]);
        };
        
        /**********************************************************************
         * If commenting is disabled globally, disable all commenting options.
         **********************************************************************/
        var commenting_enabled_globally = $("#form-widgets-globally_enabled-0").attr("checked");
        if (commenting_enabled_globally === false) {
            $.disableSettings([
                $('#formfield-form-widgets-anonymous_comments'),
                $('#formfield-form-widgets-text_transform'),
                $('#formfield-form-widgets-captcha'),
                $('#formfield-form-widgets-show_commenter_image'),
                $('#formfield-form-widgets-moderator_notification_enabled'),
                $('#formfield-form-widgets-user_notification_enabled')
            ]);
        };
        $("input[name='form.widgets.globally_enabled:list']").live("click", function (e) {
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
                    $('#formfield-form-widgets-user_notification_enabled')
                ]);
            }
        });

        /**********************************************************************
         * Remove the disabled attribute from all form elements before 
         * submitting the form. Otherwise the z3c.form will raise errors on
         * the required attributes.
         **********************************************************************/
        $("input[name='form.buttons.save']").live("click", function (e) {
            e.preventDefault();
            $('#formfield-form-widgets-anonymous_comments').removeAttr('disabled');
            $('#formfield-form-widgets-text_transform').removeAttr('disabled');
            $('#formfield-form-widgets-captcha').removeAttr('disabled');
            $('#formfield-form-widgets-show_commenter_image').removeAttr('disabled');
            $('#formfield-form-widgets-moderator_notification_enabled').removeAttr('disabled');
            $('#formfield-form-widgets-user_notification_enabled').removeAttr('disabled');
            $(this).parents().filter("form").submit();
        });           

	});

    //#JSCOVERAGE_ENDIF

}(jQuery));
