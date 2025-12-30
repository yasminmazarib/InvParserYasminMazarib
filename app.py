from fastapi import FastAPI, UploadFile, File
import oci
import base64
from db_util import init_db, save_inv_extraction
import time

app = FastAPI()

# Load OCI config from ~/.oci/config
config = oci.config.from_file()
doc_client = oci.ai_document.AIServiceDocumentClient(config)

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    pdf_bytes = await file.read()

    # Base64 encode PDF
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    document = oci.ai_document.models.InlineDocumentDetails(
        data=encoded_pdf
    )

    request = oci.ai_document.models.AnalyzeDocumentDetails(
        document=document,
        features=[
            oci.ai_document.models.DocumentFeature(
                feature_type="KEY_VALUE_EXTRACTION"
            ),
            oci.ai_document.models.DocumentClassificationFeature(
                max_results=5
            )
        ]
    )

    # ⏱️ מדידת זמן
    start_time = time.time()
    response = doc_client.analyze_document(request)
    end_time = time.time()
    prediction_time = end_time - start_time

    # 📦 בינתיים נחזיר רק זמן חיזוי (כי data עדיין לא מחושב בקוד הזה)
    result = {
        "confidence": "1",
        "data": None,
        "dataConfidence": None,
        "predictionTime": prediction_time
    }

    # אפשר לשמור את התוצאה בבסיס הנתונים (כשזה יהיה רלוונטי)
    # save_inv_extraction(result)

    return result


if __name__ == "__main__":
    import uvicorn

    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8080)
