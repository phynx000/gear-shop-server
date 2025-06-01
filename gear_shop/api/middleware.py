import traceback

class PrintExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            print("==== Exception caught in middleware ====")
            traceback.print_exc()
            raise
