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
        jq.post(target, params, function(data) {
            jq(row).fadeOut("normal", function() {
                jq(this).remove();
            });
        });
    });


    /*****************************************************************
     * Bulk actions
     *****************************************************************/
    jq('form.bulkactions').submit(function(e) {
        e.preventDefault();
        var target = jq(this).attr('action');
        var params = jq(this).serialize();
		var valArray = jq('input:checkbox:checked');
        jq.post(target, params, function(data) {
            valArray.each(function () {
				row = jq(this).parent().parent();
	            row.fadeOut("normal", function() {
	               row.remove();
	            });
            });
        });
    });


});