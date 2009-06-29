jq(document).ready(function() {

    /*****************************************************************
     * Check or uncheck all checkboxes
     *****************************************************************/
	jq("input[name='check_all']").click(function(){
	      if(jq(this).val()==0){
	        jq(this).parents("table")
	               .find("input:checkbox")
	               .attr("checked","checked")
	      }
	      else{
	        jq(this).parents("table")
	               .find("input:checkbox")
	               .attr("checked","")
	      }
    });


    /*****************************************************************
     * Comment actions (delete, publish)
     *****************************************************************/
    jq('form.background-form').submit(function(e) {
        e.preventDefault();
        var target = jq(this).attr('action');
        var params = jq(this).serialize();
        var cell = jq(this).parent().get(0);
        var row = jq(cell).parent().get(0);
        var currentFilter = jq(this).find("[name='form.button.Filter']").attr("value");
        var currentAction = jq(this).attr("class");
        jq.post(target, params, function(data) {
			if (currentAction == 'background-form workflow_action' && currentFilter == '') {
                alert("NotImplementedError: AJAX switch workflow state")
			}
			else {
				jq(row).fadeOut("normal", function(){
					jq(this).remove();
				});
			}
        });
    });


    /*****************************************************************
     * Bulk actions (delete, publish)
     *****************************************************************/
    jq('form.bulkactions').submit(function(e) {
        e.preventDefault();
        var target = jq(this).attr('action');
        var params = jq(this).serialize();
		var valArray = jq('input:checkbox:checked');
        var currentFilter = jq(this).find("[name='form.button.Filter']").attr("value");
		var currentAction = jq(this).find("[name='form.select.BulkAction']").val();
        if (valArray.length) {
            jq.post(target, params, function(data) {
                valArray.each(function () {
					// if bulkaction is delete, or the current filter is
					// pending (because then publish also removes the comment),
					// remove all selected comments.
                    if (currentAction == 'delete' || currentFilter == 'pending') {
                        row = jq(this).parent().parent();
                        row.fadeOut("normal", function() {
                           row.remove();
                        });
                    }
					// if bulkaction is publish and there is no current filter,
					// change the workflow action
					if (currentAction == 'publish') {
                        alert("NotImplementedError: AJAX switch workflow state")
					}
                });
            });
        } else {
			// The user has submitted a bulk action, but no comment
			// was selected.
			// Todo: nicer and translated message
            alert("You haven't selected anything for this bulk action.");
        }
    });

});