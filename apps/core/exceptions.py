from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Custom exception handler for consistent API error responses."""
    response = exception_handler(exc, context)

    if response is not None:
        error_payload = {
            "status_code": response.status_code,
            "errors": [],
        }
        if isinstance(response.data, dict):
            for field, value in response.data.items():
                if isinstance(value, list):
                    for v in value:
                        error_payload["errors"].append({"field": field, "message": str(v)})
                else:
                    error_payload["errors"].append({"field": field, "message": str(value)})
        elif isinstance(response.data, list):
            for item in response.data:
                error_payload["errors"].append({"field": "non_field_errors", "message": str(item)})
        else:
            error_payload["errors"].append({"field": "detail", "message": str(response.data)})

        response.data = error_payload
    else:
        response = Response(
            {"status_code": 500, "errors": [{"field": "server", "message": "Internal server error"}]},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
