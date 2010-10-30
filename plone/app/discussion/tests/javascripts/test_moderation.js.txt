/* TEST SETUP */

module("comments", {
    setup: function () {
		// <form>
        //   <table id="review-comments">
        //     <tbody>
        //       <tr>
        //         <td>
        //           <a href="http://localhost:8080/Plone/front-page/++conversation++default/1285339036601284">My comment</a>
        //         </td>
        //         <td class="actions">
        //           <input id="1285339036601284" class="context comment-publish-button" type="submit" value="Publish" name="form.button.Publish" />
        //           <input id="1285339036601284" class="destructive comment-delete-button" type="submit" value="Delete" name="form.button.Delete" />
        //         </td>
        //       </tr>
        //     </tbody>
        //   </table>
        // </form>
        var review_table = $(document.createElement("form"))
            .append($(document.createElement("table"))
                .attr("id", "review-comments")
                .append($(document.createElement("tbody"))
                    .append($(document.createElement("tr"))
                        .append($(document.createElement("td"))
						    .append($(document.createElement("a"))
							    .text("My comment.")
                                .attr("href", "http://localhost:8080/Plone/front-page/++conversation++default/1285339036601284")
                            )
						)
                        .append($(document.createElement("td"))
                            .append($(document.createElement("input"))
                                .attr("id", "1285339036601284")
								.attr("value", "Publish") 
								.attr("name", "form.button.Publish")
                            )
                            .append($(document.createElement("input"))
                                .attr("id", "1285339036601284")
								.attr("value", "Delete") 
                                .attr("name", "form.button.Delete")
                            )
							.addClass("actions")
                        )
                    )
                )
            );
        $(document.body).append(review_table);	
    },
    teardown: function () {
        $("form").remove();			
    }
});


/* TESTS */

test("Delete a single comment", function(){
    expect(1);
    stop();
	var delete_button = $(".actions").children("input[name='form.button.Delete']");
    delete_button.trigger('click');
	start();
    equals($("#1285339036601284").attr("name", "form.button.Delete").length, 0, "The comment row should have been deleted.");
});


test("Publish a single comment", function(){	
    expect(1);
    var publish_button = $(".actions").children("input[name='form.button.Publish']");
    publish_button.trigger('click');
    equals($("#1285339036601284").attr("name", "form.button.Publish").length, 0, "The comment row should have been removed since the comment has been published.");
});
