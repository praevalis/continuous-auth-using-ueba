from fastapi import APIRouter

from src.env import vars
from src.dtos import InferenceRequest, InferenceResponse
from src.inference import generate_features, process_input, predict

router = APIRouter()

@router.post('/infer', response_model=InferenceResponse)
async def inference_endpoint(payload: InferenceRequest) -> InferenceResponse:
    try:
        df = generate_features(payload.user, payload.computer, payload.timestamp)
        global_tensor, user_tensor = process_input(df)
        risk_score = predict(global_tensor, user_tensor)

        return InferenceResponse(
            anomaly=risk_score >= vars.THRESHOLD,
            risk_score=risk_score
        )

    except Exception as e:
        print(f'Error in inference endpoint: {e}')
        raise e