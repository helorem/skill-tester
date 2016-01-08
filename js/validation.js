function validate(form, rules, callback)
{
	var fields = $("input, textarea, select");
	var res = true;
	var data = {};
	var field;
	var $field;
	var name;
	for (var i in fields.get())
	{
		field = fields[i];
		res &= validate_field(field, rules);
		$field = $(field);
		name = $field.attr("name");
		if (name)
		{
			if ($field.attr("type") == "radio")
			{
				if ($field.prop("checked"))
				{
					data[name] = $field.val();
				}
			}
			else
			{
				if (name.match(/\[\]$/))
				{
					if (!(name in data))
					{
						data[name] = [];
					}
					data[name].push($field.val());
				}
				else
				{
					data[name] = $field.val();
				}
			}
		}
	}

	if (res)
	{
		callback(data);
	}
	else
	{
		show_message("Certains champs sont invalides", "error");
	}
}

function show_field_error(elm, error)
{
	var field_div = elm;
	while (!field_div.hasClass("field"))
	{
		field_div = field_div.parent();
		if (field_div.prop("tagName") == "form")
		{
			//No field div, exit
			return
		}
	}
	field_div.addClass("error");
	field_div.attr("data-content", error);
	field_div.popup();
}

function hide_field_error(elm)
{
	var field_div = elm;
	while (!field_div.hasClass("field"))
	{
		field_div = field_div.parent();
		if (field_div.prop("tagName") == "form")
		{
			//No field div, exit
			return
		}
	}
	field_div.removeAttr("data-content");
	field_div.popup("destroy");
	field_div.removeClass("error");
}

function validation_not_empty(elm)
{
	var res = true;
	if (elm.val() == "")
	{
		show_field_error(elm, "Ce champ ne doit pas etre vide");
		res = false;
	}
	else
	{
		hide_field_error(elm);
	}
	return res;
}

function validate_field(dom_elm, rules)
{
	var elm = $(dom_elm);
	var name = elm.attr("name");
	var res = true;
	if (name in rules)
	{
		var validations = rules[name];
		var require_ok = true;
		for (var key in validations["require"])
		{
			var val = $('select[name=' + key + '],input[name=' + key + '],textarea[name=' + key + ']').val();
			if (val != validations["require"][key])
			{
				require_ok = false;
			}
		}
		if (require_ok)
		{
			for (var i in validations["tests"])
			{
				if (!validations["tests"][i](elm))
				{
					res = false;
					break;
				}
			}
		}
	}
	return res;
}

