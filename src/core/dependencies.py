from services.model_service import ModelService

model_service_instance = ModelService()

def get_model_service():
    return model_service_instance