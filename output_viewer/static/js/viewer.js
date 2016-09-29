$("body").ready(function(){
	$("a[data-preview$='.png']").popover({
		"content": function(){
			var link = $(this);
			var img_url = link.attr("data-preview");
			var img = document.createElement("img");
			$(img).attr('src', img_url).attr('width', "100%");
			return img;
		},
		"trigger": "hover",
		"placement": "left",
		"html": true
	});

	var right_arrow = "right_arrow";
	var down_arrow = "down_arrow";

	$(".disclosable").each(function() {
		var self = $(this);
		var title_area = $(document.createElement("div")).addClass("disclosable_header");
		var text = self.attr("data-title");
		title_area.append(text);
		title_area.addClass("right_arrow");
		self.prepend(title_area);
		title_area.nextAll().hide();
		title_area.click(function(){
			if (title_area.hasClass(down_arrow)) {
				title_area.text("Show " + text).nextAll().hide()
			} else {
				title_area.text("Hide " + text).nextAll().show();
			}
			title_area.toggleClass(down_arrow).toggleClass(right_arrow);
		});
	});
});