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
        if (valArray.length) {
            jq.post(target, params, function(data) {
                valArray.each(function () {
					/* Remove all selected lines. */
                    var row = jq(this).parent().parent();
                    row.fadeOut("normal", function() {
                       row.remove();
                    });
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