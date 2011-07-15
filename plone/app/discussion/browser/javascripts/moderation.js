/******************************************************************************
 * 
 * jQuery functions for the plone.app.discussion bulk moderation.
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
         * Delete a single comment.
         **********************************************************************/
        $("input[name='form.button.Delete']").click(function (e) {
            e.preventDefault();
            var button = $(this);
            var row = $(this).parent().parent();
            var form = $(row).parents("form");
            var path = $(row).find("[name='selected_obj_paths:list']").attr("value");
            var target = path + "/@@moderate-delete-comment";
            var comment_id = $(this).attr("id");
            $.ajax({
                type: "GET",
                url: target,
                success: function (msg) {
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
                error: function (msg) {
                    alert("Error sending AJAX request:" + target);
                }
            });
        });
        
        
        /**********************************************************************
         * Publish a single comment.
         **********************************************************************/
        $("input[name='form.button.Publish']").click(function (e) {
            e.preventDefault();
            var button = $(this);
            var row = $(this).parent().parent();
            var form = $(row).parents("form");
            var path = $(row).find("[name='selected_obj_paths:list']").attr("value");
            var target = path + "/@@moderate-publish-comment";
            $.ajax({
                type: "GET",
                url: target,
                success: function (msg) {
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
                error: function (msg) {
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
                $.post(target, params, function (data) {
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
                error: function (msg) {
                    alert("Error getting full comment text:" + target);
                }
            });
        });
    
    });
    
    //#JSCOVERAGE_ENDIF
    
}(jQuery));
