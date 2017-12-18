$(function() {
	var iconHtml = '<span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span></span>';

	for(var name in datetimeFields) {
		var pickerName = name + "_picker";

		var root = $("#" + name);
		var container = $('<div class="input-group date" id="' + pickerName + '"></div>');
		var input = $("#id_" + name);
		container.insertBefore(input);
		input.appendTo(container);
		$(iconHtml).appendTo(container);

		$("#" + pickerName).datetimepicker(datetimeFields[name]);
	}
});
