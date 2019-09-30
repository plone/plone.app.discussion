/******************************************************************************
 *
 * jQuery functions for the plone.app.discussion bulk moderation.
 *
 ******************************************************************************/
/* global require, alert */
/* jshint quotmark: false */

if(require === undefined){
    require = function(reqs, torun){  // jshint ignore:line
        'use strict';
        return torun(window.jQuery);
    };
}

require([  // jshint ignore:line
    'jquery'
], function ($) {
    'use strict';
    // This unnamed function allows us to use $ inside of a block of code
    // without permanently overwriting $.
    // http://docs.jquery.com/Using_jQuery_with_Other_Libraries

    //#JSCOVERAGE_IF 0

    /**************************************************************************
     * Document Ready Function: Executes when DOM is ready.
     **************************************************************************/
    $(document).ready(function () {

        /**********************************************************************
         * Delete a single comment.
         **********************************************************************/
        $("input[name='form.button.Delete']").click(function (e) {
            e.preventDefault();
            var row = $(this).parent().parent();
            var path = $(row).find("[name='selected_obj_paths:list']").attr("value");
            var auth_key = $('input[name="_authenticator"]').val();
            var target = path + "/@@moderate-delete-comment?_authenticator=" + auth_key;
            $.ajax({
                type: "GET",
                url: target,
                success: function (msg) {  // jshint ignore:line
                    // fade out row
                    $(row).fadeOut("normal", function () {
                        $(this).remove();
                    });
                    // reload page if all comments have been removed
                    var comments = $("table#review-comments > tbody > tr");
                    if (comments.length === 1) {
                        location.reload();
                    }
                },
                error: function (msg) {  // jshint ignore:line
                    alert("Error sending AJAX request:" + target);
                }
            });
        });


        /**********************************************************************
         * Publish a single comment.
         **********************************************************************/
        $("input[name='form.button.Publish']").click(function (e) {
            e.preventDefault();
            var row = $(this).parent().parent();
            var path = $(row).find("[name='selected_obj_paths:list']").attr("value");
            var auth_key = $('input[name="_authenticator"]').val();
            var target = path + "/@@moderate-publish-comment?_authenticator=" + auth_key;
            var moderate = $(this).closest("fieldset").attr("id") == "fieldset-moderate-comments";
            $.ajax({
                type: "GET",
                url: target,
                success: function (msg) {  // jshint ignore:line
                    if (moderate) {
                        // fade out row
                        $(row).fadeOut("normal", function () {
                            $(this).remove();
                        });
                        // reload page if all comments have been removed
                        var comments = $("table#review-comments > tbody > tr");
                        if (comments.length === 1) {
                            location.reload();
                        }
                    } else {
                        location.reload();
                    }
                },
                error: function (msg) {  // jshint ignore:line
                    alert("Error sending AJAX request:" + target);
                }
            });
        });


        /**********************************************************************
         * Reject a single comment.
         **********************************************************************/
        $("input[name='form.button.Reject']").click(function (e) {
            e.preventDefault();
            var row = $(this).parent().parent();
            var path = $(row).find("[name='selected_obj_paths:list']").attr("value");
            var auth_key = $('input[name="_authenticator"]').val();
            var target = path + "/@@moderate-reject-comment?_authenticator=" + auth_key;
            var moderate = $(this).closest("fieldset").attr("id") == "fieldset-moderate-comments";
            $.ajax({
                type: "GET",
                url: target,
                success: function (msg) {  // jshint ignore:line
                    if (moderate) {
                        // fade out row
                        $(row).fadeOut("normal", function () {
                            $(this).remove();
                        });
                        // reload page if all comments have been removed
                        var comments = $("table#review-comments > tbody > tr");
                        if (comments.length === 1) {
                            location.reload();
                        }
                    } else {
                        location.reload();
                    }
                },
                error: function (msg) {  // jshint ignore:line
                    alert("Error sending AJAX request:" + target);
                }
            });
        });


        /**********************************************************************
         * Bulk actions for comments (delete, publish)
         **********************************************************************/
        $("input[name='form.button.BulkAction']").click(function (e) {
            e.preventDefault();
            var form = $(this).parents("form");
            var target = $(form).attr('action');
            var params = $(form).serialize();
            var valArray = $('input:checkbox:checked');
            var selectField = $(form).find("[name='form.select.BulkAction']");
            if (selectField.val() === '-1') {
                // XXX: translate message
                alert("You haven't selected a bulk action. Please select one.");
            } else if (valArray.length === 0) {
                // XXX: translate message
                alert("You haven't selected any comment for this bulk action." +
                      "Please select at least one comment.");
            } else {
                $.post(target, params, function (data) {  // jshint ignore:line
                    valArray.each(function () {
                        /* Remove all selected lines. */
                        var row = $(this).parent().parent();
                        row.fadeOut("normal", function () {
                            row.remove();
                        });
                    });
                    // reload page if all comments have been removed
                    var comments = $("table#review-comments > tbody > tr");
                    if (comments.length <= valArray.length) {
                        location.reload();
                    }
                });
                // reset the bulkaction select
                selectField.find("option[value='-1']").attr('selected', 'selected');
            }
        });


        /**********************************************************************
         * Check or uncheck all checkboxes from the batch moderation page.
         **********************************************************************/
        $("input[name='check_all']").click(function () {
            if ($(this).val() === '0') {
                $(this).parents("table")
                       .find("input:checkbox")
                       .attr("checked", "checked");
                $(this).val("1");
            } else {
                $(this).parents("table")
                       .find("input:checkbox")
                       .attr("checked", "");
                $(this).val("0");
            }
        });


        /**********************************************************************
         * Show full text of a comment in the batch moderation page.
         **********************************************************************/
        $(".show-full-comment-text").click(function (e) {
            e.preventDefault();
            var target = $(this).attr("href");
            var td = $(this).parent();
            $.ajax({
                type: "GET",
                url: target,
                data: "",
                success: function (data) {
                    // show full text
                    td.replaceWith("<td>" + data + "</td>");
                },
                error: function (msg) {  // jshint ignore:line
                    alert("Error getting full comment text:" + target);
                }
            });
        });


        /**********************************************************************
         * Comments approved: Load history for approved date.
         **********************************************************************/
        $(".last-history-entry").each(function() {
            $(this).load($(this).attr("data-href") + " .historyByLine", function() {
                let currententry = $(this).children(".historyByLine").first();
                $(this).html(currententry);
            });
        });

    });

    //#JSCOVERAGE_ENDIF

});
