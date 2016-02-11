function get_url_param(name)
{
	var res = false;
	var results = new RegExp('[\?&]' + name + '=([^&#]+)').exec(window.location.href);
	if (results)
	{
		res = results[1];
	}
	return res;
}

function parseQCode(raw)
{
	var res = raw;

	var re = new RegExp("(<.+?>)", "gm")
	var blocks = res.split(re);
	var blk_type = null;
	var block;
	for (var i in blocks)
	{
		block = blocks[i];
		if (block.startsWith("</"))
		{
			blk_type = null;
			block = "";
		}
		else if (block.startsWith("<"))
		{
			blk_type = block;
			block = "";
		}
		else
		{
			switch (blk_type)
			{
				case "<code>":
					block = "<textarea class='code_part'>" + block.trim() + "</textarea>";
					break;

				default:
					block = block.replace(/\n/g, "<br />");
					break;
			}
		}
		blocks[i] = block;
	}

	res = blocks.join("");
	return res;
}

function show_message(msg, type)
{
	/**
	  * Show a message after a validation.
	  * @param msg the message displayed
	  * @param type the type of message in (error, success). If not specified, the remaining message is cleared.
	  */
	var $msg_box = $("#message_box");
	if (type == "error")
	{
		$msg_box.html('<div class="ui visible error message"><div class="header">Erreur</div><p>' + msg + '</p></div>');
	}
	else if (type == "success")
	{
		$msg_box.html('<div class="ui visible success message"><div class="header">Succes</div><p>' + msg + '</p></div>');
	}
	else
	{
		$msg_box.html('');
	}
}

function render_code(language, prefix_url, callback)
{
	if (!prefix_url)
	{
		prefix_url = "";
	}

	//TODO improve (make static? conf file ?)
	////////////////////// language mapping
	var language_mapping = {
			"c++" : "clike",
			"c" : "clike",
			"java" : "clike",
			"objective-c" : "clike",
			"scala" : "clike",
			"kotlin" : "clike",
			"ceylon" : "clike"
		};

	var language_js = language;
	if (language_js in language_mapping)
	{
		language_js = language_mapping[language_js];
	}

	//TODO improve (make static? conf file ?)
	////////////////////// mode mapping
	var mode_mapping = {
			"c++" : "text/x-c++src",
			"c" : "text/x-csrc",
			"java" : "text/x-java",
			"objective-c" : "text/x-objectivec",
			"scala" : "text/x-scala",
			"kotlin" : "text/x-kotlin",
			"ceylon" : "text/x-ceylon"
		};

	var mode = language;
	if (mode in mode_mapping)
	{
		mode = mode_mapping[mode];
	}

	var fct = function(mode) {
			var data = {
					"mode" : mode,
					"indentUnit" : 4,
					"readOnly" : true,
					"lineNumbers" : true,
					"viewportMargin" : 0
				};

			$("textarea.code_part").each(function() {
					CodeMirror.fromTextArea(this, data);
				});
			if (callback)
			{
				callback();
			}
		};


	var res = $.getScript(prefix_url + "libs/codemirror/mode/" + language_js + "/" + language_js + ".js");
	res.done(function() {fct(mode)});
	res.fail(function() {fct(null)});
}

function display_header(text, path_prefix)
{
	if (!path_prefix)
	{
		path_prefix = ".";
	}

	var $root = $('body');
	var $div = $('<div class="logo header" />');
	$div.append($('<img class="logo" />').attr('src', path_prefix + "/assets/capfi.png"));
	$div.append($('<h1 />').text(text));
	$root.prepend($div);
}
