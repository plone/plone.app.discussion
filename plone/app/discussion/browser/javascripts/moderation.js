jq(document).ready(function() {

    /*****************************************************************
     * Check all checkboxes.
     *****************************************************************/
	jq("input[name='check_all']").click(function(){
	      if(jq(this).val()==0){
	        jq(this).parents("table")
	               .find("input:checkbox")
	               .attr("checked","checked")
	               .val("1");
	      }
	      else{
	        jq(this).parents("table")
	               .find("input:checkbox")
	               .attr("checked","")
	               .val("0");
	      }
    });

 });