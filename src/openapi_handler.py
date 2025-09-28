from fastapi.openapi.utils import get_openapi

class OpenAPIHandler:
    def __init__(self, app):
        self.app = app
        # ---! openapi metodunu override et
        self.app.openapi = self.custom_openapi
    
    def custom_openapi(self):
        if self.app.openapi_schema:
            return self.app.openapi_schema
        
        openapi_schema = get_openapi(
            title="Call Center Insight with Swagger",
            version="1.0.0",
            description="""
            ## Production-Ready FastAPI with Comprehensive Swagger Documentation
            
            This API provides a complete call center insight system with the following features:
            
            ### Features
            * **Base Analysis**: Create, read, update, and delete base analysis
            * **Issue Analysis**: Create, read, update, and delete issue analysis
            * **Authentication**: Bearer token authentication
            * **Validation**: Comprehensive input validation
            * **Error Handling**: Proper HTTP status codes
            
            ### Authentication
            This API uses Bearer token authentication. Include the following header in your requests:
            ```
            Authorization: Bearer your-secret-token
            ```
            """,
            routes=self.app.routes,
            contact={
                "name": "API Support",
                "url": "https://yourcompany.com/contact",
                "email": "support@yourcompany.com",
            },
            license_info={
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT",
            },
            servers=[
                {
                    "url": "http://localhost:8083",
                    "description": "Development server"
                }
            ]
        )
        
        # ---! Components anahtarının var olduğundan emin ol
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        
        # ---! Güvenlik şemasını ekle
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter your bearer token"
            }
        }
        
        # ---! Global güvenlik gereksinimini ekle
        openapi_schema["security"] = [{"BearerAuth": []}]
        
        self.app.openapi_schema = openapi_schema
        return openapi_schema
