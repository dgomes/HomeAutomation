def jsonpCallback(request, data):
	callback = request.args.get('callback')

	if callback:
		callback = callback[0]
		data = '%s(%s);' % (callback, data)
		return data
	return "callback({'error': 'no callback defined'})"

