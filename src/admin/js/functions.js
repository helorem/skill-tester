function test_logged()
{
	var res = $.ajax({
            url : "../api/admin/is_logged",
            dataType : "json",
            async : false
        });
	res.done(function(data) {
			if (!data)
			{
				document.location.assign("login.htm");
			}
		});
	res.fail(function(data) {
			switch (data.status)
			{
				case 403:
					document.location.assign("login.htm");
					break;
				default:
					console.error(data.responseText);
			}
		});
}

