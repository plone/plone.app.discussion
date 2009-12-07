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
        var currentFilter = jq(form).find("[name='form.button.Filter']").attr("value");
        jq.ajax({
            type: "GET",
            url: target,
			data: "workflow_action=publish",
            success: function(msg){
				if (currentFilter == 'pending') {
                    // fade out row
                    jq(row).fadeOut("normal", function(){
                        jq(this).remove();
                    });
				} else {
					// fade out button
					jq(button).fadeOut("normal", function(){
						jq(this).remove();
					});
				}
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
        var currentFilter = jq(form).find("[name='form.button.Filter']").attr("value");
        var currentAction = jq(form).find("[name='form.select.BulkAction']").val();
        var selectField = jq(form).find("[name='form.select.BulkAction']");
        if (valArray.length) {
            jq.post(target, params, function(data) {
                valArray.each(function () {
                    // if bulkaction is delete, or the current filter is
                    // pending (because then publish also removes the comment),
                    // remove all selected comments.
                    if (currentAction == 'delete' || currentFilter == 'pending') {
                        var row = jq(this).parent().parent();
                        row.fadeOut("normal", function() {
                           row.remove();
                        });
                    }
                    // bulkaction is publish and there is no current filter
                    if (currentAction == 'publish' && currentFilter == '') {
                        // remove the publish button
                        var row = jq(this).parent().parent();
                        var form = row.find("form.workflow_action");
                        var publishButton = row.find(".comment-publish-button");
                        var selectField = row.find("input:checkbox");
                        jq(publishButton).fadeOut("normal", function(){
                            jq(form).remove();
                        });
                        // reset the select fields
                        selectField.attr("checked","");
                    }
                });
            });
        } else {
            // The user has submitted a bulk action, but no comment
            // was selected.
            // Todo: nicer and translated message
            alert("You haven't selected anything for this bulk action.");
        }
        // reset the bulkaction select
        selectField.find("option[value='-1']").attr( 'selected', 'selected' );
    });

});