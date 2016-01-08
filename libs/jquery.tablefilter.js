(function($) {
	$.tablefilter = function ($table, settings) {
		this.filters = {};
		this.$table = $table;
		this.settings = $.extend({}, $.tablefilter.defaults, settings);
		this.filter_row = $('<tr class="tablefilter"></tr>');
		this.refresh();
	};

	$.tablefilter.prototype = {

		clear: function(index) {
			var sel = this.filter_row.find("select[name='" + index + "']");
			sel.val("");
			this.filter(sel);
		},

		refresh: function() {
			var self = this;
			this.filter_row.empty();
			var thead = this.$table.find('thead');
			var filterCells = thead.find('th');
			var cells;
			var val_list;
			var sel;
			var th;
			for (var i = 0; i < filterCells.length; ++i)
			{
				if ($(filterCells[i]).hasClass("no-filter"))
				{
					sel = "";
				}
				else
				{
					cells = this.$table.find('tr td:nth-of-type(' + (i + 1) + ')');
					val_list = cells.map(function(){ return $(this).text(); }).get();
					val_list = jQuery.unique(val_list)

					sel = $('<select name="' + (i + 1) + '" class="ui dropdown search"></select>');
					sel.append('<option value="">' + this.settings.placeholder + '</option>')
					$.each(val_list, function() {
							sel.append("<option value='" + this + "'>" + this + "</option>")
						});
					sel.bind('change.tablefiler', function() { self.filter($(this)); });
				}

				th = $('<th class="' + this.settings.th_classname + '"></th>');
				th.append(sel);
				this.filter_row.append(th);
			}
			thead.append(this.filter_row);
			thead.find('.ui.dropdown').dropdown();
		},

		filter: function(sel) {
			index = sel.attr("name");
			var val = sel.val();
			this.filters[index] = val;
			var filters = this.filters;

			var rows = this.$table.find('tbody tr');
			rows.each(function() {
					var row = $(this);
					var match = true;
					for (var i in filters)
					{
						filter_val = filters[i];
						if (filter_val != "")
						{
							var cell = row.find('td:nth-of-type(' + i + ')');
							if (cell.text() != filter_val)
							{
								match = false;
								break;
							}
						}
					}
					if (match)
					{
						row.show();
					}
					else
					{
						row.hide();
					}
				});

			if (val != "")
			{
				var th = this.filter_row.find('th:nth-of-type(' + index + ')');
				th.find('.selection.dropdown').addClass(this.settings.used_classname);
				var icon = $('<i class="' + this.settings.icon + '" name="' + index + '"></i>');
				var self = this;
				icon.bind('click.tablefilter', function() { self.clear($(this).attr('name')); });
				th.append(icon);
			}
			else
			{
				var th = this.filter_row.find('th:nth-of-type(' + index + ')');
				var dd = th.find('.selection.dropdown');
				dd.removeClass(this.settings.used_classname);
				dd.dropdown('restore defaults');
				th.find('i').remove();
			}
		}

	};

	$.tablefilter.DEBUG = false;

	$.tablefilter.defaults = {
		debug: $.tablefilter.DEBUG,
		used_classname: "used",
		icon: "remove circle outline icon",
		placeholder: "-- Filtre --",
		th_classname: "no-sort"
	};

	$.fn.tablefilter = function(settings) {
		var table, previous;
		return this.each(function() {
			table = $(this);
			previous = table.data('tablefilter');
			if (previous) {
				previous.refresh();
			}
			else
			{
				table.data('tablefilter', new $.tablefilter(table, settings));
			}
		});
	};

})(window.Zepto || window.jQuery);
