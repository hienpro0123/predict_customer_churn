from typing import Any

import requests

from config.settings import (
    API_TIMEOUT_SECONDS,
    DATABRICKS_TOKEN,
    DATABRICKS_URL,
    DISABLE_OUTBOUND_PROXY,
    FEATURE_COLUMNS,
    REQUEST_HEADERS,
)
from utils.helpers import clamp_probability, get_error_message, normalize_prediction_value


def _create_databricks_session() -> requests.Session:
    session = requests.Session()
    if DISABLE_OUTBOUND_PROXY:
        session.trust_env = False
    return session


def build_payload(features: dict[str, Any]) -> dict[str, Any]:
    ordered_record = {column: features[column] for column in FEATURE_COLUMNS}
    return {"dataframe_records": [ordered_record]}


def extract_prediction(result: Any) -> tuple[int, float]:
    if isinstance(result, dict):
        prediction = next(
            (
                result.get(key)
                for key in ("prediction", "predicted_label", "label", "class")
                if result.get(key) is not None
            ),
            None,
        )
        probability = next(
            (
                result.get(key)
                for key in ("probability", "probabilities", "score", "churn_probability")
                if result.get(key) is not None
            ),
            None,
        )

        if isinstance(probability, list) and probability:
            probability = probability[-1]
        elif isinstance(probability, dict) and probability:
            probability = (
                probability.get("1")
                or probability.get(1)
                or probability.get("true")
                or probability.get(True)
                or max(probability.values())
            )

        if probability is not None:
            probability = clamp_probability(probability)

        if prediction is None and probability is not None:
            return int(probability >= 0.5), probability

        if prediction is not None:
            normalized_prediction = normalize_prediction_value(prediction)
            fallback_probability = clamp_probability(normalized_prediction)
            return normalized_prediction, probability if probability is not None else fallback_probability

    if isinstance(result, (int, float)):
        numeric_value = float(result)
        if 0.0 <= numeric_value <= 1.0:
            return int(numeric_value >= 0.5), numeric_value
        return int(numeric_value), clamp_probability(int(numeric_value))

    raise ValueError("Unexpected prediction format returned by Databricks Model Serving.")


def parse_databricks_error(response: requests.Response) -> tuple[str, str]:
    raw_message = get_error_message(response)

    try:
        payload = response.json()
    except ValueError:
        technical_detail = f"Databricks API error {response.status_code}: {raw_message}"
        return "Không thể đọc phản hồi lỗi từ Databricks API.", technical_detail

    error_code = payload.get("error_code", "UNKNOWN_ERROR")
    message = payload.get("message", raw_message)
    stack_trace = payload.get("stack_trace", "")
    technical_detail = (
        f"HTTP {response.status_code}\n"
        f"Error code: {error_code}\n"
        f"Message: {message}\n\n"
        f"Stack trace:\n{stack_trace or 'Không có stack trace'}"
    )

    if "need to call fit or load_model beforehand" in message or "NotFittedError" in stack_trace:
        user_message = (
            "Endpoint Databricks đã nhận dữ liệu, nhưng model đang deploy chưa sẵn sàng dự đoán. "
            "Bạn cần kiểm tra lại model version hoặc artifact trên Databricks."
        )
        return user_message, technical_detail

    user_message = f"Databricks API đang báo lỗi {response.status_code}. Vui lòng kiểm tra endpoint hoặc dữ liệu đầu vào."
    return user_message, technical_detail


def query_databricks(
    features: dict[str, Any],
) -> tuple[bool, str, str | None, tuple[int, float] | None]:
    if not DATABRICKS_URL or not DATABRICKS_TOKEN:
        return (
            False,
            "Thiếu cấu hình DATABRICKS_URL hoặc DATABRICKS_TOKEN trong file .env.",
            None,
            None,
        )

    payload = build_payload(features)
    headers = {
        **REQUEST_HEADERS,
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    }

    try:
        response = _create_databricks_session().post(
            DATABRICKS_URL,
            headers=headers,
            json=payload,
            timeout=API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return False, "Kết nối Databricks bị timeout. Vui lòng thử lại.", None, None
    except requests.exceptions.ConnectionError as exc:
        return False, "Không thể kết nối tới Databricks API.", str(exc), None
    except requests.exceptions.HTTPError:
        user_message, technical_detail = parse_databricks_error(response)
        return False, user_message, technical_detail, None
    except requests.exceptions.RequestException as exc:
        return False, "Yêu cầu tới Databricks API thất bại.", str(exc), None

    try:
        response_json = response.json()
    except ValueError:
        return False, "Databricks API trả về dữ liệu không đúng định dạng JSON.", response.text, None

    predictions = response_json.get("predictions")
    if not predictions:
        return (
            False,
            "Phản hồi từ Databricks không chứa trường 'predictions'.",
            str(response_json),
            None,
        )

    try:
        parsed_result = extract_prediction(predictions[0])
    except (TypeError, ValueError, KeyError) as exc:
        return False, "Không đọc được kết quả dự đoán từ Databricks.", str(exc), None

    return True, "", None, parsed_result

def query_databricks_batch(
    features_list: list[dict[str, Any]],
) -> tuple[bool, str, str | None, list[tuple[int, float]] | None]:
    if not features_list:
        return False, "Khong co du lieu de du doan.", None, None

    if not DATABRICKS_URL or not DATABRICKS_TOKEN:
        return (
            False,
            "Thieu cau hinh DATABRICKS_URL hoac DATABRICKS_TOKEN trong file .env.",
            None,
            None,
        )

    ordered_records = [{column: row[column] for column in FEATURE_COLUMNS} for row in features_list]
    payload = {"dataframe_records": ordered_records}
    headers = {
        **REQUEST_HEADERS,
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    }

    try:
        response = _create_databricks_session().post(
            DATABRICKS_URL,
            headers=headers,
            json=payload,
            timeout=API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return False, "Ket noi Databricks bi timeout. Vui long thu lai.", None, None
    except requests.exceptions.ConnectionError as exc:
        return False, "Khong the ket noi toi Databricks API.", str(exc), None
    except requests.exceptions.HTTPError:
        user_message, technical_detail = parse_databricks_error(response)
        return False, user_message, technical_detail, None
    except requests.exceptions.RequestException as exc:
        return False, "Yeu cau toi Databricks API that bai.", str(exc), None

    try:
        response_json = response.json()
    except ValueError:
        return False, "Databricks API tra ve du lieu khong dung dinh dang JSON.", response.text, None

    predictions = response_json.get("predictions")
    if not predictions:
        return (
            False,
            "Phan hoi tu Databricks khong chua truong 'predictions'.",
            str(response_json),
            None,
        )

    parsed_results: list[tuple[int, float]] = []
    try:
        for prediction_item in predictions:
            parsed_results.append(extract_prediction(prediction_item))
    except (TypeError, ValueError, KeyError) as exc:
        return False, "Khong doc duoc ket qua batch prediction tu Databricks.", str(exc), None

    if len(parsed_results) != len(features_list):
        return (
            False,
            "So luong ket qua tra ve khong khop voi so dong dau vao.",
            f"Input rows: {len(features_list)}, predictions: {len(parsed_results)}",
            None,
        )

    return True, "", None, parsed_results
