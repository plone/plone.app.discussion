jq(document).ready(function() {

    /*****************************************************************
     * Check or uncheck all checkboxes
     *****************************************************************/
    jq("input[name='check_all']").click(function(){
          if(jq(this).val()==0){
            jq(this).parents("table")
                   .find("input:checkbox")
                   .attr("checked","checked");
            jq(this).val("1");
          }
          else{
            jq(this).parents("table")
                   .find("input:checkbox")
                   .attr("checked","");
            jq(this).val("0");
          }
    });


    /*****************************************************************
     * Delete comment
     *****************************************************************/
    jq("input[name='form.button.Delete']").click(function(e) {
        e.preventDefault();
        var button = jq(this);
        var row = jq(this).parent().parent();
        var form = jq(row).parents("form");
        var path = jq(row).find("input:checkbox").attr("value");
        var target = path + "/@@moderate-delete-comment";
        var comment_id = jq(this).attr("id");
        jq.ajax({
            type: "GET",
            url: target,
            success: function(msg){
                // fade out row
                jq(row).fadeOut("normal", function(){
                    jq(this).remove();
                });
            },
            error: function(msg){
                alert("Error sending AJAX request:" + target);
            }
        });
    });

    /*****************************************************************
     * Publish comment
     *****************************************************************/
    jq("input[name='form.button.Publish']").click(function(e) {
        e.preventDefault();
        var button = jq(this);
        var row = jq(this).parent().parent();
        var form = jq(row).parents("form");
        var path = jq(row).find("input:checkbox").attr("value");
        var target = path + "/@@moderate-publish-comment";
        jq.ajax({
            type: "GET",
            url: target,
            data: "workflow_action=publish",
            success: function(msg){
                // fade out row
                jq(row).fadeOut("normal", function(){
                    jq(this).remove();
                });
            },
            error: function(msg){
                alert("Error sending AJAX request:" + target);
            }
        });
    });


    /*****************************************************************
     * Bulk actions (delete, publish)
     *****************************************************************/
    jq("input[name='form.button.BulkAction']").click(function(e) {
        e.preventDefault();
        var form = jq(this).parents("form")
        var target = jq(form).attr('action');
        var params = jq(form).serialize();
        var valArray = jq('input:checkbox:checked');
        var selectField = jq(form).find("[name='form.select.BulkAction']");
        if (selectField.val() == '-1') {
            // XXX: translate message
            alert("You haven't selected a bulk action. Please select one.");
        } else if (valArray.length == 0) {
            // XXX: translate message
            alert("You haven't selected any comment for this bulk action. Please select at least one comment.");
        } else {
            jq.post(target, params, function(data) {
                valArray.each(function () {
                    /* Remove all selected lines. */
                    var row = jq(this).parent().parent();
                    row.fadeOut("normal", function() {
                       row.remove();
                    });
                });
            });
            // reset the bulkaction select
            selectField.find("option[value='-1']").attr( 'selected', 'selected' );
        }
    });

    /*****************************************************************
     * Show full text of a comment.
     *****************************************************************/
    jq(".show-full-comment-text").click(function(e) {    
        e.preventDefault();
        var target = jq(this).attr("href");
        var td = jq(this).parent();
        jq.ajax({
            type: "GET",
            url: target,
            data: "",
            success: function(data){
                // show full text
                td.replaceWith("<td>" + data + "</td>");
            },
            error: function(msg){
                alert("Error getting full comment text:" + target);
            }
        });        
    });

});